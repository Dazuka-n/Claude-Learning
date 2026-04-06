"""Audio analysis MCP server backed by the AssemblyAI SDK.

Two tools are exposed over stdio so Claude Desktop can launch the
server as a subprocess:

  * transcribe_audio  - run a full AssemblyAI transcription with
                        summarization, topics, sentiment, speakers,
                        and language detection. Caches the resulting
                        transcript in a module-level global.
  * get_audio_data    - return slices of that cached transcript
                        (summary, speakers, sentiment, topics) based
                        on boolean flags.

The two-tool design lets Claude run an expensive transcription once
and then ask cheap follow-up questions against the same transcript.
"""

from __future__ import annotations

import os
from typing import Any

import assemblyai as aai
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if _API_KEY:
    aai.settings.api_key = _API_KEY

mcp = FastMCP("audio-analysis-toolkit")

# Cached transcript shared between the two tools.
LATEST_TRANSCRIPT: aai.Transcript | None = None
LATEST_AUDIO_PATH: str | None = None


@mcp.tool()
def transcribe_audio(audio_path: str) -> dict:
    """Transcribe a local audio file with AssemblyAI and cache the result.

    Use this tool whenever the user wants to transcribe, analyze, or
    "open" an audio or video file from disk. It runs AssemblyAI with
    every major insight feature enabled (summarization, IAB topic
    categories, sentiment analysis, speaker diarization, automatic
    language detection) and stores the full transcript object in
    server memory so follow-up questions can be answered cheaply via
    `get_audio_data` without re-running the model.

    Args:
        audio_path: Absolute or relative path to a local audio/video
            file (mp3, wav, m4a, mp4, etc.).

    Returns:
        A dict with the detected language, total duration in seconds,
        and a `sentences` list. Each sentence is `{text, start, end}`
        where start/end are millisecond timestamps.
    """
    global LATEST_TRANSCRIPT, LATEST_AUDIO_PATH

    if not _API_KEY:
        raise RuntimeError(
            "ASSEMBLYAI_API_KEY is not set. Add it to your environment "
            "or to a .env file next to server.py."
        )
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    config = aai.TranscriptionConfig(
        summarization=True,
        iab_categories=True,
        sentiment_analysis=True,
        speaker_labels=True,
        language_detection=True,
    )
    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(audio_path)

    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"AssemblyAI failed: {transcript.error}")

    LATEST_TRANSCRIPT = transcript
    LATEST_AUDIO_PATH = audio_path

    sentences = [
        {"text": s.text, "start": s.start, "end": s.end}
        for s in transcript.get_sentences()
    ]
    return {
        "audio_path": audio_path,
        "language": getattr(transcript, "language_code", None),
        "duration_seconds": (transcript.audio_duration or 0),
        "num_sentences": len(sentences),
        "sentences": sentences,
    }


@mcp.tool()
def get_audio_data(
    summary: bool = False,
    speakers: bool = False,
    sentiment: bool = False,
    topics: bool = False,
) -> dict:
    """Return cached insights from the most recently transcribed audio file.

    Use this tool AFTER `transcribe_audio` has been called at least
    once. Set whichever boolean flags the user is asking about - you
    can combine them in a single call to fetch several insight types
    at once. If no flag is set, all four are returned.

    Args:
        summary: Include AssemblyAI's auto-generated summary.
        speakers: Include speaker-diarized utterances (speaker label
            plus text and timestamps).
        sentiment: Include sentence-level sentiment analysis results
            (POSITIVE / NEUTRAL / NEGATIVE with confidence).
        topics: Include the IAB content categories the model detected.

    Returns:
        A dict whose keys correspond to the flags you set.
    """
    if LATEST_TRANSCRIPT is None:
        raise RuntimeError(
            "No transcript cached yet. Call `transcribe_audio` first."
        )

    # If the caller passed nothing, return everything.
    if not any([summary, speakers, sentiment, topics]):
        summary = speakers = sentiment = topics = True

    transcript = LATEST_TRANSCRIPT
    out: dict[str, Any] = {"audio_path": LATEST_AUDIO_PATH}

    if summary:
        out["summary"] = getattr(transcript, "summary", None)

    if speakers:
        utterances = []
        for u in (transcript.utterances or []):
            utterances.append(
                {
                    "speaker": u.speaker,
                    "text": u.text,
                    "start": u.start,
                    "end": u.end,
                }
            )
        out["speakers"] = utterances

    if sentiment:
        sentiment_results = []
        for s in (transcript.sentiment_analysis or []):
            sentiment_results.append(
                {
                    "text": s.text,
                    "sentiment": str(s.sentiment),
                    "confidence": float(s.confidence),
                    "start": s.start,
                    "end": s.end,
                }
            )
        out["sentiment"] = sentiment_results

    if topics:
        topic_results: list[dict] = []
        iab = getattr(transcript, "iab_categories", None)
        if iab is not None:
            summary_map = getattr(iab, "summary", {}) or {}
            for label, score in summary_map.items():
                topic_results.append(
                    {"topic": label, "relevance": float(score)}
                )
            topic_results.sort(key=lambda x: x["relevance"], reverse=True)
        out["topics"] = topic_results

    return out


if __name__ == "__main__":
    # stdio transport: Claude Desktop launches this script as a child
    # process and talks to it over stdin/stdout.
    mcp.run(transport="stdio")
