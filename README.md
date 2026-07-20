# AI Research Agent — MCP Server + Supervisor/Worker Multi-Agent System

An AI research assistant that can search the web, read `.txt`/`.pdf` files, and remember facts within a conversation — built as an **MCP (Model Context Protocol) server**, with a **Supervisor agent** that routes each query to specialized worker agents, and full tracing/logging of every step.

## Features

- 🔍 **Web search** — fetches current/live information via SerpAPI
- 📄 **File reading** — reads `.txt` and `.pdf` files and answers questions about their content
- 🧠 **Session memory** — recalls facts (like your name) shared earlier in the conversation
- 🧩 **MCP server** — exposes the agent as a standard MCP tool + resource, connectable from any MCP client (Claude Desktop, custom clients, etc.)
- 🧑‍💼 **Supervisor + Worker agents** — a Supervisor routes each query to a `FileWorker` and/or `SearchWorker`, and hands off results between them for multi-hop questions
- 📝 **Full tracing** — every Supervisor/Worker hop and every individual tool call is logged with timestamps
- 🔁 **Self-healing retries** — automatically retries and recovers from occasional malformed tool-call responses from the LLM, without crashing or surfacing an error to the user

## What This Project Demonstrates

| Requirement | Implementation |
|---|---|
| Custom MCP server: 1 resource + 1 tool | `mcp_server/server.py` — resource `research://about` (`mcp_server/resources.py`), tool `research(query)` (`mcp_server/tools.py`) |
| Connect an MCP client to the server | `client/client.py` — a stdio `ClientSession` that spawns the server and calls the `research` tool |
| Supervisor + 2 worker agents | `agent/supervisor.py` routes each query to `FileWorker` and/or `SearchWorker` (`workers/`) based on keywords in the query |
| Hand-offs between agents | For file + web questions, `FileWorker`'s output is passed as context into `SearchWorker` |
| Tracing every step across the agent graph | `tracing/tracer.py` logs every Supervisor → Worker hop to `logs/agent_trace.log`; `hooks/logger.py` logs every underlying tool call to `logs/tool_calls.log` |

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
      └──► SearchWorker (workers/search_worker.py) → agent/research_service.py → tools/serp_search.py → SerpAPI
```

Every hop through Supervisor/FileWorker/SearchWorker is logged to `logs/agent_trace.log`, and every underlying tool call (`read_txt_file`, `read_pdf_file`, `serp_search`) is separately logged to `logs/tool_calls.log`.

## Tech Stack

| Purpose | Tool / Library |
|---|---|
| LLM | Groq — `llama-3.3-70b-versatile` |
| Agent framework | LangChain (`create_agent`) |
| Agent-to-LLM connector | `langchain-groq` |
| MCP protocol | `mcp` (FastMCP) |
| Web search | SerpAPI (`google-search-results`) |
| PDF reading | `pypdf` |
| Env config | `python-dotenv` |

## Project Structure

```
research_agent/
├── mcp_server/
│   ├── server.py         # Starts the FastMCP server (stdio transport)
│   ├── tools.py           # Registers the "research" tool
│   └── resources.py        # Registers the "research://about" resource
├── client/
│   └── client.py           # Standalone MCP client that talks to the server
├── agent/
│   ├── builder.py            # Builds the LangChain agent (LLM + tools + system prompt)
│   ├── supervisor.py          # Routes queries to FileWorker / SearchWorker
│   ├── research_service.py     # Runs the agent with retry + self-healing recovery
│   └── file_service.py          # Answers questions about a specific file
├── workers/
│   ├── file_worker.py            # Reads a .txt/.pdf file mentioned in the query
│   └── search_worker.py           # Runs a web-search-backed research query
├── plugins/
│   ├── txt_reader.py               # .txt file reader tool
│   └── pdf_reader.py                # .pdf file reader tool
├── tools/
│   ├── serp_search.py                 # Web search tool (LangChain @tool)
│   └── search_service.py               # Calls SerpAPI directly
├── memory/
│   └── session_memory.py                # Stores conversation history for the session
├── tracing/
│   └── tracer.py                          # Logs every Supervisor/Worker hop
├── hooks/
│   └── logger.py                           # Logs every individual tool call
├── logs/
│   ├── agent_trace.log                      # Agent-graph trace (auto-generated)
│   └── tool_calls.log                        # Tool-level log (auto-generated)
├── sample_files/
│   ├── python.txt
│   └── ai.pdf
├── test_supervisor.py                          # Quick manual test of the Supervisor
├── test_workers.py                              # Quick manual test of the two workers
├── main.py                                       # Standalone LangChain chat agent (single-agent version)
├── prompts.md                                     # System prompt / rules the agent follows
└── requirements.txt
```

## Setup

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your own API keys:
   ```bash
   cp .env.example .env
   ```
   Then fill in:
   ```
   GROQ_API_KEY=your_key_here
   SERPAPI_API_KEY=your_key_here
   ```
   - Get a Groq key: https://console.groq.com/keys
   - Get a SerpAPI key: https://serpapi.com/manage-api-key

## Running It

**Option A — run the MCP client + server together (recommended)**
```bash
python -m client.client
```
This spawns the MCP server over stdio and gives you a `You :` prompt. Every query is sent to the server's `research` tool, which the Supervisor routes to the right worker(s).

**Option B — run the MCP server alone** (e.g. to connect from Claude Desktop or another MCP client)
```bash
python -m mcp_server.server
```

**Option C — run the standalone single-agent version** (no MCP, no supervisor)
```bash
python main.py
```

**Option D — quick manual tests without MCP**
```bash
python test_supervisor.py
python test_workers.py
```

## Example Queries

- `Who invented Python?` → routed to `SearchWorker` only
- `Read sample_files/python.txt` → routed to `FileWorker`
- `Read sample_files/python.txt and tell me the latest version` → routed to both `FileWorker` and `SearchWorker` (multi-hop: file is read first, then its content is used as context for the web search)

Check `logs/agent_trace.log` and `logs/tool_calls.log` afterwards to see the full trace of what the Supervisor and each tool did.

## Known Limitations

- No cost/latency optimization yet — every task uses the same model regardless of complexity
- No structured output validation — responses are plain text, not a validated schema
- MCP server currently exposes one resource and one tool; no MCP prompts are registered yet

## Security Note

`.env` holds your real API keys — never commit or share it. It's already listed in `.gitignore`.
