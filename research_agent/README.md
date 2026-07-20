# Research Agent — MCP Server + Supervisor/Worker Multi-Agent System

This is the Week 5 build. It wraps last week's research agent behind an MCP
server, adds a Supervisor agent that routes each query to specialised worker
agents, and logs every step for tracing.

## What this project demonstrates

| Requirement | Implementation |
|---|---|
| Custom MCP server: 1 resource + 1 tool | `mcp_server/server.py` — resource `research://about` (`mcp_server/resources.py`), tool `research(query)` (`mcp_server/tools.py`) |
| Connect MCP server to a client | `client/client.py` — a stdio `ClientSession` that spawns the server and calls the `research` tool |
| Supervisor + ≥2 worker agents | `agent/supervisor.py` routes each query to `FileWorker` and/or `SearchWorker` (`workers/`) based on keywords in the query |
| Tracing every tool call across the agent graph | `tracing/tracer.py` logs every Supervisor → Worker step to `logs/agent_trace.log`; `hooks/logger.py` logs every underlying tool call (file read, web search) to `logs/tool_calls.log` |

## Architecture

```
Client (client/client.py)
      │  MCP stdio
      ▼
MCP Server (mcp_server/server.py)
      │  exposes tool "research" + resource "research://about"
      ▼
SupervisorAgent (agent/supervisor.py)
      │  decides which worker(s) to call based on the query
      ├──► FileWorker   (workers/file_worker.py)   → plugins/pdf_reader.py, plugins/txt_reader.py
      └──► SearchWorker (workers/search_worker.py) → agent/research_service.py → tools/serp_search.py
```

Every hop through Supervisor/FileWorker/SearchWorker is logged to
`logs/agent_trace.log` (via `tracing/tracer.py`), and every underlying tool
call (`read_txt_file`, `read_pdf_file`, `serp_search`) is separately logged
to `logs/tool_calls.log` (via `hooks/logger.py`).

## Project Structure

```
research_agent/
├── mcp_server/
│   ├── server.py        # Starts the FastMCP server (stdio transport)
│   ├── tools.py          # Registers the "research" tool
│   └── resources.py       # Registers the "research://about" resource
├── client/
│   └── client.py          # Standalone MCP client that talks to the server
├── agent/
│   └── supervisor.py       # Routes queries to FileWorker / SearchWorker
├── workers/
│   ├── file_worker.py       # Reads a .txt/.pdf file mentioned in the query
│   └── search_worker.py      # Runs a web-search-backed research query
├── plugins/
│   ├── txt_reader.py          # .txt file reader tool
│   └── pdf_reader.py           # .pdf file reader tool
├── tools/
│   └── serp_search.py           # Web search tool (SerpAPI)
├── tracing/
│   └── tracer.py                 # Logs every Supervisor/Worker hop
├── hooks/
│   └── logger.py                  # Logs every individual tool call
├── logs/
│   ├── agent_trace.log             # Agent-graph trace (auto-generated)
│   └── tool_calls.log               # Tool-level log (auto-generated)
├── sample_files/
│   ├── python.txt
│   └── ai.pdf
├── test_supervisor.py                 # Quick manual test of the Supervisor
├── test_workers.py                     # Quick manual test of the two workers
├── main.py                              # (Week 4 leftover) standalone LangChain chat agent, not part of this week's MCP pipeline
└── requirements.txt
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your real API keys:
   ```bash
   cp .env.example .env
   ```
   Fill in `GROQ_API_KEY` and `SERPAPI_API_KEY`.
   - Groq key: https://console.groq.com/keys
   - SerpAPI key: https://serpapi.com/manage-api-key

## Run it

**Option A — run the MCP client + server together**
```bash
python -m client.client
```
This spawns the MCP server over stdio and gives you a `You :` prompt. Every
query is sent to the server's `research` tool, which is routed by the
Supervisor to the right worker(s).

**Option B — run the MCP server alone (e.g. to connect from Claude Desktop)**
```bash
python -m mcp_server.server
```

**Option C — quick manual tests without MCP**
```bash
python test_supervisor.py
python test_workers.py
```

## Example queries

- `Who invented Python?` → routed to `SearchWorker` only
- `Read sample_files/python.txt` → routed to `FileWorker` (+ `SearchWorker` to summarize)
- `Read sample_files/python.txt and tell me the latest version` → routed to
  both `FileWorker` and `SearchWorker` (multi-hop: file content is read
  first, then used as context for the web search)

Check `logs/agent_trace.log` and `logs/tool_calls.log` afterwards to see the
full trace of what the Supervisor and each tool did.

## Security Note

`.env` holds your real API keys — never commit or share it. It's already in
`.gitignore`.
