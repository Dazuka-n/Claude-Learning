# 04 - Audio Analysis Toolkit MCP

A FastMCP server that gives Claude Desktop two audio superpowers via
the [AssemblyAI](https://www.assemblyai.com) SDK: a one-shot
**transcribe + analyze** call, and a cheap **insight lookup** that
reuses the cached transcript for follow-up questions.

## Project purpose

Let a Claude Desktop user point at any local audio or video file and
have a normal conversation about it — "what's this clip about", "who
said the angry part", "what topics does it cover", "summarize it" —
without making Claude juggle the AssemblyAI SDK itself or pay for a
fresh transcription on every question. The first call uploads + runs
the model; every follow-up reads from a server-side cache.

## The two tools

### `transcribe_audio(audio_path)`
Reads a local file, calls `aai.Transcriber` with **every** insight
feature switched on:

- `summarization=True`
- `iab_categories=True`
- `sentiment_analysis=True`
- `speaker_labels=True`
- `language_detection=True`

Stores the resulting `aai.Transcript` object in a module-level global
(`LATEST_TRANSCRIPT`) and returns sentences with millisecond
timestamps so Claude can quote or seek into the audio.

### `get_audio_data(summary, speakers, sentiment, topics)`
Reads from the cached transcript and returns whichever insight types
the boolean flags ask for. Combine flags freely. If no flag is set, it
returns all four. This is the cheap follow-up tool Claude reaches for
after the expensive `transcribe_audio` call has run once.

## stdio vs SSE — and why this server uses stdio

MCP supports two main transports:

| Transport | How it works                                                                 | Best for                                                                                       |
|-----------|------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| **stdio** | Host launches the server as a child process and pipes JSON-RPC over stdin/stdout. | Local-only servers that ship as a script and need zero network setup. Claude Desktop's native mode. |
| **SSE**   | Server runs as a long-lived HTTP service; clients connect to `/sse`.         | Servers shared between multiple clients, remote servers, browser-based hosts, dev/iteration loops. |

Claude Desktop is designed around **stdio**: you describe the command
in `claude_desktop_config.json`, Claude spawns it on startup, and the
server's lifetime is tied to Claude's. There's no port to manage, no
firewall prompt, and the server inherits the env vars Claude was told
to pass. For a single-user local tool like this one, stdio is the
right call — it's the path of least friction for Claude Desktop and
keeps secrets (the AssemblyAI API key) off any network interface.

We'd switch to SSE if multiple hosts (Cursor + Claude Desktop +
notebooks) needed to share the same long-running transcript cache.
Here, the cache is intentionally per-process, so stdio is a perfect
fit.

## File structure

```
04-audio-analysis-toolkit/
├── server.py                    # FastMCP, stdio transport, both tools
├── requirements.txt
├── claude_desktop_config.json   # Drop-in Developer config snippet
├── .env.example
└── README.md
```

## Setup

1. Python 3.10+.
2. Install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   # source .venv/bin/activate     # macOS / Linux
   pip install -r requirements.txt
   ```
3. Get an API key from <https://www.assemblyai.com/dashboard/signup>.
4. Copy the example env file and fill in the key:
   ```bash
   cp .env.example .env
   # then edit .env and replace your_key_here
   ```

## Wire it into Claude Desktop

1. Open Claude Desktop → Settings → Developer → **Edit Config**. This
   opens `claude_desktop_config.json` in your editor.
   - macOS path:   `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows path: `%APPDATA%\Claude\claude_desktop_config.json`
2. Paste the contents of this project's `claude_desktop_config.json`
   into the file, merging the `mcpServers` block if you already have
   other servers configured.
3. Update the `args` path so it points at *your* absolute path to
   `server.py`, and replace `your_key_here` in `env` with your real
   AssemblyAI key.
4. Fully **quit and relaunch** Claude Desktop. On startup it will
   spawn `python server.py` as a child process and discover the two
   tools. You should see a small hammer / tools icon in the chat
   composer indicating that an MCP server is connected.

The exact snippet to paste:

```json
{
  "mcpServers": {
    "audio-analysis-toolkit": {
      "command": "python",
      "args": [
        "C:\\Users\\Office\\Desktop\\Projects\\Claude-Learning\\MCP-servers-build\\04-audio-analysis-toolkit\\server.py"
      ],
      "env": {
        "ASSEMBLYAI_API_KEY": "your_key_here"
      }
    }
  }
}
```

## How to test it

Once Claude Desktop is restarted, prompts that should fire each tool:

- **Triggers `transcribe_audio`:**
  > "Can you transcribe `C:\\clips\\interview.mp3` for me?"
  > "Analyze this audio file: /Users/me/podcast.wav"
- **Triggers `get_audio_data` (after a transcription is cached):**
  > "Who were the speakers and what was the overall sentiment?"
  > "Just give me the summary and the topics."
  > "What was the angriest sentence in that clip?"

Claude will ask you to approve each tool call the first time.

## Example conversation

```
you   > Transcribe C:\clips\product-demo.mp3 and tell me what it's about.

Claude > [calls transcribe_audio(audio_path="C:\\clips\\product-demo.mp3")]
         → returns 47 sentences, language=en, duration=312s
        I've transcribed the 5-minute clip. It's a product demo with
        two speakers walking through an analytics dashboard. Want me
        to pull the summary and topics?

you   > Yes, and tell me who said what.

Claude > [calls get_audio_data(summary=True, speakers=True, topics=True)]
         → returns:
           summary: "Two presenters demo a real-time analytics
                     dashboard, focusing on funnel visualization
                     and anomaly alerts..."
           speakers: [
             {"speaker": "A", "text": "Welcome everyone, today we're..."},
             {"speaker": "B", "text": "Thanks Alex. Let me jump into..."},
             ...
           ]
           topics: [
             {"topic": "Technology&Computing>Software", "relevance": 0.93},
             {"topic": "Business>Marketing", "relevance": 0.71}
           ]
        Speaker A (the host) opens and closes the demo; Speaker B
        does most of the deep dive. Top topics are software and
        marketing. Here's the summary: ...

you   > Was anyone negative at any point?

Claude > [calls get_audio_data(sentiment=True)]
         → 41 NEUTRAL, 5 POSITIVE, 1 NEGATIVE
        Almost entirely neutral or positive. The single negative
        sentence (~02:14) was Speaker B saying "the old dashboard
        was painfully slow"—it's framed as a contrast with the new
        product, not a real complaint.
```

Notice how AssemblyAI is only called **once**. Every follow-up uses
the in-memory transcript via `get_audio_data`, so they're instant and
free.

## What I learned

- **stdio is the default for Claude Desktop, and that's a feature.**
  No port collisions, no firewall popups, secrets travel via the
  spawned process's env block instead of a network socket, and the
  server's lifecycle is tied 1:1 to the client's. For a single-user
  local tool this is dramatically simpler than running an SSE daemon.
- **SSE is what you reach for when the server needs a life of its
  own** — long-lived caches, multiple connected hosts, remote
  deployment, or rapid iteration where you want to restart the server
  without restarting the host. The earlier projects in this repo use
  SSE for exactly that reason; this one doesn't need it.
- **Claude Desktop discovers tools via the MCP handshake at startup.**
  When Claude launches, it spawns each server in `mcpServers`, sends
  an `initialize` request, then `tools/list`. The descriptions it
  gets back are *literally my Python docstrings*. After that, Claude
  decides on its own when to emit a `tools/call` based on the user's
  message — there is no routing code on the client side.
- **Pair an "expensive setup" tool with a "cheap query" tool.**
  Splitting `transcribe_audio` (slow, paid, network) from
  `get_audio_data` (instant, in-memory) lets the agent run a
  natural multi-turn conversation against a single transcript.
  Claude figures out the order from the docstrings ("Use this AFTER
  `transcribe_audio` has been called…").
- **Module-level globals are fine for stdio servers.** Because Claude
  Desktop owns the process lifetime, the `LATEST_TRANSCRIPT` global
  lives exactly as long as the conversation context that needs it.
  In an SSE server I'd want a real keyed cache instead, since
  multiple clients could collide.
