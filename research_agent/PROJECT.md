# Project Review — Week 5 (MCP + Multi-Agent Systems)

Reviewed against the assignment checklist:
- MCP protocol fundamentals, transport, capabilities
- Building MCP servers: resources, tools, and **prompts**
- Connecting MCP clients (Claude Code / Cursor / custom)
- Multi-agent orchestration: supervisor + worker, hand-offs
- Tool design: clear names, narrow scopes, good errors
- Agent debugging: tracing tool calls, **replaying transcripts**, isolating failures
- **Cost & latency strategy**
- Recap: **structured outputs and output validation as guardrails**

## ✅ What was already correct

| Requirement | Where | Status |
|---|---|---|
| Custom MCP server exposing a resource + tool | `mcp_server/server.py`, `resources.py`, `tools.py` | Working (`research://about` resource, `research` tool) |
| MCP client connected to the server | `client/client.py` | Working (custom stdio client) |
| Supervisor + worker routing to ≥2 sub-agents | `agent/supervisor.py`, `workers/search_worker.py`, `workers/file_worker.py` | Working (routes to File, Search, or both) |
| Tool call logging | `hooks/logger.py` → `logs/tool_calls.log` | Working, every plugin/search tool call logged |
| Supervisor/worker decision logging | `tracing/tracer.py` → `logs/agent_trace.log` | Working |
| Tool design (naming, docstrings, try/except) | `plugins/`, `tools/` | Reasonable — narrow, single-purpose tools with clear docstrings |

## ❌ What was missing (now fixed)

### 1. MCP **prompts** were never implemented
You had resources and tools, but the assignment explicitly lists all three
MCP primitives ("exposing resources, tools, **and prompts**"). Nothing in
the codebase used `@mcp.prompt()`.

**Fixed**: added `mcp_server/prompts.py` with two prompt templates
(`research_query`, `summarize_file`), registered in `mcp_server/server.py`.

### 2. No structured-output / output-validation guardrail
The recap topic ("structured outputs and output validation as agent
guardrails") had no corresponding code anywhere — the supervisor returned
raw LLM/tool text straight through with no schema or validation step.

**Fixed**: added `agent/schemas.py` with a Pydantic `AgentAnswer` model
that enforces: non-empty answers, a length cap, and a check against raw
unsummarized tool-payload leakage. `agent/supervisor.py` now routes every
return path through `validate_answer(...)` before responding.

### 3. No cost & latency strategy
This was a required topic with zero documentation or design decisions
addressing it anywhere in the repo (no notes on model choice, retry
budget, or where LLM calls vs. deterministic code are used).

**Fixed**: added `COST_STRATEGY.md`, documenting: why routing is
keyword-based instead of LLM-based, why only `SearchWorker` calls the LLM,
why `llama-3.3-70b-versatile` on Groq was chosen (latency), the capped
retry budget, and search-result trimming before it hits the LLM context.

### 4. No way to replay a transcript for debugging
You had two log files (`tool_calls.log`, `agent_trace.log`) but no
tooling to reconstruct/replay a session from them — "replaying
transcripts, isolating failures" was only half-covered (logging existed,
replay didn't).

**Fixed**: added `debug/replay.py`. Run:
```bash
python -m debug.replay              # full merged timeline
python -m debug.replay --last 20    # last 20 events
python -m debug.replay --component SearchWorker
```
It merges both log files into one chronological timeline and flags
`FAILED` tool-call entries as `<-- FAILURE POINT`.

## 🔒 Security issue found and fixed

The uploaded zip contained a **real `.env` file with live API keys**
(Groq + SerpAPI) instead of only `.env.example`. This has been removed
from the corrected project. **Rotate both keys** if that zip was ever
shared or committed anywhere, then use `.env.example` to create a fresh
local `.env`.

## 🧹 Cleanup done (not functional gaps, but worth knowing)

- Removed the committed `venv/` folder (~thousands of files) — a
  virtual environment should never be zipped/committed; `requirements.txt`
  is what recreates it.
- `requirements.txt` was saved as **UTF-16**, which breaks
  `pip install -r requirements.txt` on most setups. Re-saved as UTF-8.
- Removed root-level `logger.py` and `tools.py` — these were an earlier,
  unused duplicate of `hooks/logger.py` and `tools/serp_search.py`. Dead
  code left in a submitted project reads as unfinished refactoring.
- Cleared committed `__pycache__/` and `.pyc` files.

## Summary

Your MCP fundamentals, server/client wiring, and supervisor/worker
orchestration were solid — that's the hardest part and it was done
correctly. What was missing was mostly the "systems maturity" layer the
assignment asks for on top of a working agent: exposing prompts (not just
tools/resources), validating output before it leaves the graph, being
explicit about cost/latency trade-offs, and being able to replay a failed
run instead of just having logs sitting there. All four are now in place.
