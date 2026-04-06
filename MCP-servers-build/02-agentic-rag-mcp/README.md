# 02 - Agentic RAG MCP

A FastMCP server that gives any MCP-aware LLM host (Cursor, Claude
Desktop, etc.) two complementary skills: a local **vector search** over
a small AI/ML FAQ knowledge base, and a **web search fallback** for
everything else. The host LLM picks which tool to call based purely on
the docstrings the server advertises — no orchestration code lives on
the client side.

## Project purpose

Show how a single MCP server can implement a tiny "agentic RAG" router
just by writing two well-described tools. The server itself is dumb —
it doesn't try to decide which tool fits the question. Instead, the
LLM host reads the tool descriptions, looks at the user's prompt, and
calls whichever tool the descriptions say is appropriate. This is the
core idea behind agentic tool use, and it's how the MCP ecosystem is
designed to scale: each server publishes capabilities, the host LLM
routes.

## Agentic routing in plain language

When you connect this server to Cursor or Claude Desktop, the host
asks the server "what tools do you have?" The server replies with two
tool definitions — each one is a `name`, an input JSON schema, and a
**description string that comes directly from the Python docstring**.

That description is the *only* thing the LLM sees about the tool. It
never reads `server.py`. So the docstring is doing the job that a
hand-written router or `if/else` block would do in a non-agentic
system:

> "USE THIS TOOL FIRST whenever the user asks about AI, ML, neural
> networks, transformers, LLMs, embeddings, vector databases, RAG…"

> "USE THIS TOOL when the user's question is NOT about AI/ML/LLMs and
> therefore cannot be answered from the local vector database…"

The LLM reads both descriptions, compares them against the user's
question, and emits a tool call for whichever one fits. If you write
vague docstrings, the LLM picks the wrong tool. If you write
intent-rich docstrings with clear "USE THIS WHEN…" phrasing, routing
works reliably without any custom logic.

## Architecture

```
        ┌──────────────────────────────┐
        │     LLM host (Cursor /        │
        │     Claude Desktop / etc.)    │
        └──────────────┬────────────────┘
                       │  MCP over SSE
                       │  http://127.0.0.1:8080/sse
                       ▼
        ┌──────────────────────────────┐
        │     FastMCP server.py         │
        │                               │
        │  ┌─────────────────────────┐  │
        │  │  vector_db_search       │  │
        │  │   ↓ embed query         │  │
        │  │   ↓ qdrant similarity   │──┼──► in-memory Qdrant
        │  │   ↓ return top_k FAQs   │  │     (10 AI/ML FAQs,
        │  └─────────────────────────┘  │      seeded at startup
        │                               │      from seed_data.py)
        │  ┌─────────────────────────┐  │
        │  │  web_search_fallback    │  │
        │  │   ↓ DDGS().text(...)    │──┼──► DuckDuckGo (live web)
        │  │   ↓ return top 3 hits   │  │
        │  └─────────────────────────┘  │
        └───────────────────────────────┘
```

`seed_data.py` owns the FAQ list and the `sentence-transformers`
embedder (`all-MiniLM-L6-v2`). At server startup it builds an
in-memory Qdrant collection, embeds every FAQ entry, and upserts the
points. `server.py` then reuses the same embedder to embed incoming
queries at request time.

## Setup

1. Python 3.10+.
2. Create a virtualenv and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   # source .venv/bin/activate     # macOS / Linux
   pip install -r requirements.txt
   ```
   The first run will download the `all-MiniLM-L6-v2` model (~80 MB).

## How to run

Start the server:
```bash
python server.py
```
It listens on `http://127.0.0.1:8080/sse`.

In a second terminal, sanity-check both tools with the bundled MCP
client:
```bash
python test_client.py
```
You should see the advertised tool list, three FAQ hits for the RAG
question, and three DuckDuckGo results for the Mars rover query.

## Connect to Cursor

Open Cursor → Settings → MCP and paste the contents of
`cursor_config.json` into your `mcp.json`:

```json
{
  "mcpServers": {
    "agentic-rag-mcp": {
      "url": "http://127.0.0.1:8080/sse",
      "transport": "sse"
    }
  }
}
```

Make sure `python server.py` is already running, then reload the MCP
panel in Cursor. You should see `vector_db_search` and
`web_search_fallback` appear under the `agentic-rag-mcp` server. (The
same JSON also works for any other MCP host that supports SSE
servers.)

## Example: each tool being triggered

**AI/ML question → `vector_db_search` is called**

```
you  > Can you explain what RAG is?
host > [calls vector_db_search(query="Can you explain what RAG is?", top_k=3)]
       → returns:
         [
           {
             "question": "What is RAG (retrieval augmented generation)?",
             "answer": "RAG is a technique where an LLM is given documents
                        retrieved from an external knowledge base at query
                        time so it can answer with grounded, up-to-date
                        information…",
             "score": 0.84
           },
           ...
         ]
host > RAG stands for retrieval augmented generation. It's a pattern
       where the LLM is given relevant documents from an external
       knowledge base at query time…
```

**Non-AI question → `web_search_fallback` is called**

```
you  > What's the latest news on the Mars rover?
host > [calls web_search_fallback(query="latest news on Mars rover")]
       → returns top 3 DuckDuckGo results with title / href / body
host > According to recent reporting, NASA's Perseverance rover…
```

The host never had to be told "use the vector DB for AI questions" —
the tool docstrings carried that instruction.

## What I learned

- **Agentic routing == well-written docstrings.** In a classic RAG
  pipeline you'd write a router function (`if "ai" in query: …`). With
  MCP you delete that function entirely and instead push the routing
  signal into each tool's description. The LLM is the router. This is
  what people mean when they call MCP "agentic" — the server exposes
  capabilities, the agent decides.
- **Be explicit, not clever.** Phrasings like "USE THIS TOOL FIRST
  WHEN…" and "USE THIS TOOL WHEN the question is NOT about X" work
  much better than describing what the tool *does* in the abstract.
  The LLM is matching intent strings, so spell out the intent.
- **Tool boundaries shape the agent's behavior.** Splitting one
  "search anything" tool into two narrower tools (vector vs. web) gave
  the host a clear decision to make and made every call traceable. A
  single fat tool would have hidden the routing inside server code and
  made debugging harder.
- **The MCP SDK client is the fastest debugging loop.** `test_client.py`
  bypasses any LLM and calls the tools directly, so I could verify
  that the server, the embedder, and DuckDuckGo all worked before
  worrying about whether Cursor's LLM was picking the right tool.
- **In-memory Qdrant is perfect for prototypes.** No daemon, no
  Docker, no persistent volume — `QdrantClient(":memory:")` plus a
  `recreate_collection` call at startup is enough to demo a real
  vector store end-to-end.
