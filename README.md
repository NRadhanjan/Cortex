
# Cortex

A multi-tool MCP (Model Context Protocol) agent that turns personal coursework notes into a queryable, RAG-powered assistant — built to understand both retrieval-augmented generation and MCP's client/server architecture from first principles.

## Architecture

User question
→ MCP Client (orchestrator)
→ Groq LLM (decides: answer directly, or call a tool?)
→ [if tool call] MCP Client → MCP Server → RAG pipeline → ChromaDB
→ Result fed back to Groq
→ Final grounded answer

## Status

- [x] RAG pipeline: notes ingestion, chunking, embedding, ChromaDB storage
- [x] MCP server exposing RAG as a `search_notes` tool
- [x] MCP client orchestrating Groq ↔ MCP server tool-calling loop
- [ ] Streamlit frontend
- [ ] Additional MCP tools (calendar scheduling, GitHub code lookup, sandboxed algorithm execution)

## Tech stack

- **LLM**: Groq API (llama-3.3-70b-versatile)
- **RAG**: LangChain, sentence-transformers (all-MiniLM-L6-v2), ChromaDB
- **MCP**: Python MCP SDK, FastMCP
- **Environment**: Google Colab + Google Drive persistence

## Why MCP

Instead of hardcoding retrieval logic directly into the chat loop, RAG is exposed as a standardized MCP tool. This makes it possible to add more capabilities (calendar, code execution, GitHub) as independent, swappable tools that any MCP-compatible client can discover and call — not just this specific chatbot.

## Setup


## Known limitations

- Runs in Google Colab; sessions are ephemeral, so the vector database is persisted to Google Drive and reloaded each session
- Free-tier Colab has usage limits and idle timeouts
- Personal notes are not included in this repo for privacy; sample structure only

## What I learned
