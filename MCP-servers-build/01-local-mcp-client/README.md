# 01 - Local MCP Client

A fully local end-to-end demo of the Model Context Protocol: a FastMCP
server that exposes a SQLite database through two tools, plus a
LlamaIndex `FunctionAgent` (driven by a local Ollama `deepseek-r1`
model) that discovers those tools at runtime and calls them in
response to natural-language queries. Nothing in this project leaves
your machine — no API keys, no cloud LLM, no remote database.

## Project purpose

Learn how MCP actually wires together by building both sides of the
connection yourself. The server side shows how trivial it is to expose
existing Python functions as MCP tools with FastMCP. The client side
shows how an agent framework (LlamaIndex) can introspect a running MCP
server, turn its tools into native function-calling tools, and let an
LLM pick the right one based on the user's request.

## Architecture

`server.py` runs a FastMCP server that owns a small SQLite file
(`demo.db`) and exposes two `@mcp.tool()`-decorated functions:
`add_data` (an INSERT into a `people` table) and `read_data` (a SELECT
of every row). It serves these tools over the SSE transport on
`http://127.0.0.1:8000/sse`. `client.py` opens a `BasicMCPClient`
against that SSE endpoint, hands it to `McpToolSpec` to convert the
remote MCP tools into LlamaIndex tools, and feeds those tools to a
`FunctionAgent` backed by `Ollama(model="deepseek-r1")`. A small
asyncio CLI loop reads user input, calls `agent.run(...)`, and prints
the agent's reply — which under the hood involves the LLM choosing a
tool, the LlamaIndex runtime invoking it through the MCP client, and
the agent summarizing the structured result back to the user.

## Setup

1. Install Python 3.10+.
2. Install [Ollama](https://ollama.com) and pull the model:
   ```bash
   ollama pull deepseek-r1
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   # source .venv/bin/activate     # macOS / Linux
   pip install -r requirements.txt
   ```

## How to run

Open **two** terminals in this folder.

Terminal 1 — start the MCP server:
```bash
python server.py
```
You should see FastMCP report that it is serving SSE on
`http://127.0.0.1:8000/sse`.

Terminal 2 — start the client:
```bash
python client.py
```
Make sure Ollama is already running in the background (it usually
auto-starts on install).

## Example interaction

```
Local MCP client ready. Type 'exit' or 'quit' to leave.

you > add a person named Ada Lovelace, age 36, profession mathematician
agent > Done. I called add_data and the server confirmed:
        "Inserted person id=1: Ada Lovelace, 36, mathematician".

you > who is in the database?
agent > I called read_data and got back one record:
        - id 1: Ada Lovelace, age 36, mathematician.

you > add Alan Turing, 41, cryptanalyst
agent > Stored. add_data returned id=2 for Alan Turing.

you > list everyone again
agent > read_data now returns two people:
        1. Ada Lovelace — 36 — mathematician
        2. Alan Turing — 41 — cryptanalyst
```

Behind the scenes, each `you >` line triggers the `FunctionAgent` to
ask the LLM which tool (if any) it should call. The LLM emits a
function call, LlamaIndex routes it through `BasicMCPClient` to the
running FastMCP server, the server executes the SQLite query, and the
JSON-serializable result flows back to the LLM so it can phrase the
final answer.

## What I learned

- **Tool docstrings are the contract.** When `McpToolSpec` converts an
  MCP tool into a LlamaIndex tool, the docstring on the
  `@mcp.tool()`-decorated function becomes the description the LLM
  sees. That description is *the only thing* Claude / deepseek-r1 /
  any other LLM uses to decide whether to call this tool. Vague
  docstrings → wrong tool calls. Concrete, intent-rich docstrings
  ("use this when the user wants to add/insert/store a person…") →
  reliable routing. The parameter names and type hints become the JSON
  schema for the arguments, so they matter just as much.
- **MCP tool schemas are auto-generated from Python type hints.** I
  didn't have to write any JSON schema by hand. FastMCP introspects
  the function signature (`name: str, age: int, profession: str`) and
  publishes a matching input schema over the wire, which the client
  then re-exposes to LlamaIndex.
- **The client/server handshake is a discovery step, not a hardcode.**
  The client never names `add_data` or `read_data` in code. It just
  connects to the SSE endpoint, asks the server "what tools do you
  have?", and dynamically wires whatever it gets back into the agent.
  Adding a new `@mcp.tool()` on the server makes it instantly
  available to the client on next startup — no client changes needed.
  This is the part of MCP that makes it feel like USB for LLM tools.
- **SSE keeps the server long-lived.** Unlike the stdio transport
  (which the client spawns as a subprocess), SSE means the server runs
  independently and any number of clients can connect to it, which is
  why we run it in its own terminal.
