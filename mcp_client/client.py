
import os
import json
from groq import Groq
from mcp import ClientSession
from mcp.client.sse import sse_client

async def ask_cortex(user_question, server_url="http://localhost:8000/sse", model="llama-3.3-70b-versatile"):
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    async with sse_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = await session.list_tools()
            groq_tools = [{
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                }
            } for t in mcp_tools.tools]

            messages = [{"role": "user", "content": user_question}]

            response = groq_client.chat.completions.create(
                model=model,
                messages=messages,
                tools=groq_tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message

            if response_message.tool_calls:
                tool_call = response_message.tool_calls[0]
                args = json.loads(tool_call.function.arguments)
                print(f"[Tool call: {tool_call.function.name} with args {args}]")

                result = await session.call_tool(tool_call.function.name, args)
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
    import asyncio
    answer = asyncio.run(ask_cortex("What is Big O notation according to my notes?"))
    print(answer)
