
# Cortex

A multi-tool MCP (Model Context Protocol) agent that turns personal coursework notes, a study planner, and GitHub project history into a single queryable assistant — built to understand both retrieval-augmented generation and MCP's client/server architecture from first principles.

## Demo

![Cortex demo](docs/demo_screenshot.png)

## Architecture

User question
→ Streamlit frontend
→ MCP Client (orchestrator)
→ Groq LLM (decides: answer directly, or call a tool?)
→ [if tool call] MCP Client → correct MCP Server → (RAG / scheduling / GitHub API)
→ Result fed back to Groq (fresh context, no tool-call transcript)
→ Final grounded answer

Three independent MCP servers, each exposing a distinct capability:

| Server | Port | Tool(s) | Purpose |
|---|---|---|---|
| `notes_server.py` | 8000 | `search_notes` | RAG over coursework notes (DSA, security, OS, DBMS, ML) via ChromaDB |
| `calendar_server.py` | 8001 | `generate_schedule` | Distributes study topics across a given number of days |
| `github_server.py` | 8002 | `list_my_projects`, `get_project_readme` | Answers questions about the user's own GitHub portfolio |

The client discovers tools from all three servers, hands them to Groq, and routes any tool call to the server that owns it.

## Status

- [x] RAG pipeline: notes ingestion, chunking, embedding, ChromaDB storage
- [x] MCP server exposing RAG as a `search_notes` tool
- [x] MCP client orchestrating Groq ↔ multiple MCP servers, with correct routing
- [x] Streamlit frontend
- [x] Calendar MCP server (multi-server tool routing)
- [x] GitHub MCP server (portfolio project lookup)
- [ ] Persistent deployment (currently runs in Google Colab)

## Tech stack

- **LLM**: Groq API (`openai/gpt-oss-120b`)
- **RAG**: LangChain, sentence-transformers (all-MiniLM-L6-v2), ChromaDB
- **MCP**: Python MCP SDK, FastMCP (SSE transport)
- **Frontend**: Streamlit
- **External data**: GitHub REST API
- **Environment**: Google Colab + Google Drive persistence, ngrok for public tunneling

## Why MCP

Instead of hardcoding retrieval, scheduling, or GitHub logic directly into the chat loop, each capability is exposed as a standardized MCP tool served by an independent process. This means new capabilities can be added as separate, swappable servers without touching the orchestration logic — the client simply discovers whatever tools are available and routes to them.

## Why Groq + model choice

Groq was chosen over a locally-hosted model (e.g. Ollama) to avoid GPU/infrastructure management in a resource-constrained Colab environment. During development, `llama-3.3-70b-versatile` showed intermittent malformed tool-call output (`tool_use_failed`) on more complex queries; switching to `openai/gpt-oss-120b` significantly improved tool-calling reliability. A retry-with-backoff mechanism was also added to handle any remaining transient failures.

## Setup

(Colab notebook link + instructions — to be added)

## Known limitations

- **Colab-based, ephemeral**: sessions and background server processes do not persist; the vector database is saved to Google Drive and copied back locally on each new session
- **Google Drive cannot host a live ChromaDB**: Drive's FUSE-based filesystem breaks SQLite's write-locking, so the database is built/updated on local disk and copied to Drive only for persistence between sessions
- **Groq free-tier rate limits**: heavy testing can exhaust the daily token quota for a given model; switching models resets the quota since limits are tracked per-model
- **Tool-calling is not 100% reliable**: some Groq-hosted models occasionally produce malformed function-call syntax; mitigated with retries but not fully eliminated
- **`get_project_readme` requires an exact repo name** and will honestly report when no README exists rather than guessing at project details
- Personal notes are not included in this repo for privacy; sample folder structure only

## What I learned

- **MCP internals**: how `tools/list` and `tools/call` work as JSON-RPC-style messages, how a client discovers tools from multiple independent servers, and how to route a tool call to the correct server based on which one advertised it
- **Multi-server orchestration**: keeping a routing table (`tool name → owning server`) so a single client can transparently combine capabilities from several MCP servers
- **Grounding discipline**: an early version of the assistant fabricated plausible-sounding project details when a GitHub tool call returned incomplete information; fixed by giving the final-answer LLM call a clean context (no prior tool-call transcript) and an explicit instruction not to infer beyond what was retrieved
- **Infrastructure debugging**: diagnosed and fixed several distinct failure modes — Google Drive's filesystem breaking SQLite writes, zombie processes holding ports after ungraceful interrupts, Streamlit's event loop conflicting with `asyncio.run()` on repeated calls, and Groq's per-model daily rate limits
- **Model selection as an engineering decision**: chose a model based on measured tool-calling reliability, not just response quality, after empirically comparing two models on identical failing queries
