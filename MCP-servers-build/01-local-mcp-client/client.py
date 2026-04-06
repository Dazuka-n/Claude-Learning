"""LlamaIndex FunctionAgent that talks to the local FastMCP server.

Make sure `python server.py` is already running in another terminal,
and that Ollama is running locally with the `deepseek-r1` model pulled:
    ollama pull deepseek-r1
Then run:
    python client.py
"""

import asyncio

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

SYSTEM_PROMPT = """\
You are a helpful assistant with access to tools that read from and
write to a local SQLite database of people.

You MUST use the provided tools to answer any question that involves
adding records or reading records. Do not make up data. Decide which
tool to call based on the user's intent:
  - If the user wants to store/add/insert a person, call `add_data`
    with name, age, and profession.
  - If the user wants to list/show/read people, call `read_data`.

After the tool returns, summarize the result clearly for the user.
"""


async def build_agent() -> FunctionAgent:
    # 1. Connect to the running MCP server over SSE
    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")

    # 2. Wrap the MCP tools as native LlamaIndex tools
    tool_spec = McpToolSpec(client=mcp_client)
    tools = await tool_spec.to_tool_list_async()

    # 3. Build the FunctionAgent with the local Ollama LLM
    llm = Ollama(model="deepseek-r1", request_timeout=120.0)
    agent = FunctionAgent(
        tools=tools,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent


async def chat_loop() -> None:
    agent = await build_agent()
    print("Local MCP client ready. Type 'exit' or 'quit' to leave.\n")
    while True:
        try:
            user_msg = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_msg:
            continue
        if user_msg.lower() in {"exit", "quit"}:
            break

        response = await agent.run(user_msg=user_msg)
        print(f"agent > {response}\n")


if __name__ == "__main__":
    asyncio.run(chat_loop())
