"""Manual MCP client to verify both tools on the running server.

Start the server first in another terminal:
    python server.py

Then run:
    python test_client.py
"""

import asyncio
import json

from mcp import ClientSession
from mcp.client.sse import sse_client

SERVER_URL = "http://127.0.0.1:8080/sse"


def _pretty(result) -> str:
    chunks = []
    for item in result.content:
        text = getattr(item, "text", None)
        if text is None:
            chunks.append(repr(item))
            continue
        try:
            chunks.append(json.dumps(json.loads(text), indent=2))
        except (ValueError, TypeError):
            chunks.append(text)
    return "\n".join(chunks)


async def main() -> None:
    async with sse_client(SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("=== Tools advertised by server ===")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description.splitlines()[0]}")
            print()

            print("=== vector_db_search('What is RAG?') ===")
            rag_result = await session.call_tool(
                "vector_db_search",
                {"query": "What is retrieval augmented generation?", "top_k": 3},
            )
            print(_pretty(rag_result))
            print()

            print("=== web_search_fallback('latest news on Mars rover') ===")
            web_result = await session.call_tool(
                "web_search_fallback",
                {"query": "latest news on Mars rover"},
            )
            print(_pretty(web_result))


if __name__ == "__main__":
    asyncio.run(main())
