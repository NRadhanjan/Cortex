
import os
import json
import asyncio
from groq import Groq, BadRequestError
from mcp import ClientSession
from mcp.client.sse import sse_client
from contextlib import AsyncExitStack

SERVERS = {
    "notes": "http://localhost:8000/sse",
    "calendar": "http://localhost:8001/sse",
    "github": "http://localhost:8002/sse",
}

async def ask_cortex(user_question, model="openai/gpt-oss-120b", max_retries=5):
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    async with AsyncExitStack() as stack:
        sessions = {}
        all_tools = []
        tool_to_server = {}

        for server_name, url in SERVERS.items():
            read, write = await stack.enter_async_context(sse_client(url))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            sessions[server_name] = session

            mcp_tools = await session.list_tools()
            for t in mcp_tools.tools:
                all_tools.append({
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema
                    }
                })
                tool_to_server[t.name] = server_name

        messages = [
            {
                "role": "system",
                "content": "You have access to multiple tools. Use `search_notes` for questions about academic concepts from the user's coursework notes. Use `generate_schedule` when the user asks for a study plan or schedule. Use `list_my_projects` or `get_project_readme` when the user asks about the user's own GitHub projects, code, or portfolio."
            },
            {"role": "user", "content": user_question}
        ]

        response_message = None
        for attempt in range(max_retries):
            try:
                response = groq_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=all_tools,
                    tool_choice="auto",
                    temperature=0.1
                )
                response_message = response.choices[0].message
                break
            except BadRequestError as e:
                if "tool_use_failed" in str(e) and attempt < max_retries - 1:
                    print(f"[Tool call malformed, retrying... attempt {attempt + 2}/{max_retries}]")
                    await asyncio.sleep(1 * (attempt + 1))
                    continue
                raise

        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            target_server = tool_to_server[tool_call.function.name]
            print(f"[Tool call: {tool_call.function.name} -> routed to '{target_server}' server, args {args}]")

            result = await sessions[target_server].call_tool(tool_call.function.name, args)
            tool_result_text = result.content[0].text

            messages.append(response_message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result_text
            })
            final = groq_client.chat.completions.create(
                model=model,
                messages=messages
            )
            return final.choices[0].message.content
        else:
            return response_message.content

if __name__ == "__main__":
    import asyncio as aio
    answer = aio.run(ask_cortex("List my GitHub projects"))
    print(answer)
