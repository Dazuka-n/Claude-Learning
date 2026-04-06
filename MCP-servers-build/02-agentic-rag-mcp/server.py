"""Agentic RAG MCP server.

Exposes two tools whose docstrings tell the host LLM exactly when to
use them:

  * vector_db_search       - for AI / ML / LLM / MCP questions
  * web_search_fallback    - for everything else

Run with:
    python server.py
The server listens on http://127.0.0.1:8080/sse
"""

from duckduckgo_search import DDGS
from fastmcp import FastMCP

from seed_data import embed, get_seeded_client

mcp = FastMCP("agentic-rag-mcp")

# Build the in-memory vector store once at import time.
_qdrant_client, _collection_name = get_seeded_client()


@mcp.tool()
def vector_db_search(query: str, top_k: int = 3) -> list[dict]:
    """Search the local AI/ML knowledge base for an answer.

    USE THIS TOOL FIRST whenever the user asks a question about
    artificial intelligence, machine learning, deep learning, neural
    networks, transformers, LLMs, embeddings, vector databases, RAG,
    fine-tuning, overfitting, or the Model Context Protocol (MCP).

    The knowledge base is a curated set of FAQ entries about AI/ML
    fundamentals. If the user's question is clearly about one of these
    topics, prefer this tool over a web search because the answers are
    authoritative and do not depend on network access.

    Args:
        query: The user's natural-language question.
        top_k: How many of the closest matches to return (default 3).

    Returns:
        A list of dicts with `question`, `answer`, and `score` keys,
        ordered from most to least relevant.
    """
    query_vector = embed(query)
    hits = _qdrant_client.search(
        collection_name=_collection_name,
        query_vector=query_vector,
        limit=top_k,
    )
    return [
        {
            "question": hit.payload["question"],
            "answer": hit.payload["answer"],
            "score": float(hit.score),
        }
        for hit in hits
    ]


@mcp.tool()
def web_search_fallback(query: str) -> list[dict]:
    """Search the live web for any topic outside the AI/ML knowledge base.

    USE THIS TOOL when the user's question is NOT about AI/ML/LLMs/MCP
    and therefore cannot be answered from the local vector database.
    Examples of when to call this tool: news, sports, weather, current
    events, general trivia, programming questions outside ML, history,
    geography, or anything time-sensitive.

    This calls DuckDuckGo and returns the top 3 organic results.

    Args:
        query: The natural-language search query.

    Returns:
        A list of up to 3 dicts with `title`, `href`, and `body` keys.
    """
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))
    return [
        {
            "title": r.get("title", ""),
            "href": r.get("href", ""),
            "body": r.get("body", ""),
        }
        for r in results
    ]


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8080)
