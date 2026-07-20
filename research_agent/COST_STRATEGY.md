# Cost & Latency Strategy

This document explains where this system spends tokens/time, and why, per
multi-agent system.

## 1. Routing is free (no LLM call)

`SupervisorAgent.route()` decides FileWorker vs SearchWorker vs both using
plain keyword matching (`.pdf`, `.txt`, `latest`, `today`, ...), not an LLM
call. Routing happens on every single request, so putting an LLM in that
path would mean paying model latency + tokens twice per query for no
quality benefit. A regex/keyword router is instant and free, and is
accurate enough for a 2-worker system.

**Trade-off**: this router can misclassify ambiguous queries (e.g. "read
the news" contains neither a file extension nor an obvious search keyword
list overlap issue). If we added a 3rd+ worker or the routing rules grew
complex, this is the point where it would become worth spending one small,
cheap LLM call (low temperature, short max_tokens, small/fast model) to
classify intent instead of hand-maintaining keyword lists.

## 2. Only one worker does real LLM reasoning

- `FileWorker` never calls the LLM. It just extracts raw text from the
  PDF/TXT (a local, free, deterministic operation) and hands it off.
- `SearchWorker` is the only place that calls the LLM (via
  `run_research` -> the LangChain agent), and only once per request,
  even in the combined file+search path (the file content is passed in
  as *context* to a single LLM call rather than summarized in one call
  and then re-reasoned about in a second call).

This means: file-only questions never touch the LLM at all in
`FileWorker.process()` itself; the LLM cost is only paid on the worker
that actually needs reasoning.

## 3. Model choice

`agent/builder.py` uses `llama-3.3-70b-versatile` on Groq. Groq's LPU
inference is chosen specifically for **latency**: it is materially faster
than typical GPU-hosted inference for the same model class, which matters
here because every user turn is synchronous (the user is waiting in a
terminal chat loop). `temperature=0` is set because this is a research/fact
tool, not creative writing — deterministic answers are cheaper to debug
and more consistent to test (see `debug/replay.py`).

## 4. Retry budget is capped, not unlimited

`get_answer_with_retry` / `run_research` cap retries at `max_retries=3`
with a 1s sleep between attempts. This bounds worst-case latency and
worst-case token spend per user turn to 3x a single call, instead of
retrying indefinitely on a persistently malformed tool call.

## 5. Web search results are capped and pre-trimmed before hitting the LLM

`tools/search_service.py` requests `num=5` results and only forwards
title/link/snippet (not full page bodies) into the LLM's context. This
keeps the token cost of the search tool's *output*, which becomes part of
the next LLM call's input, small and bounded regardless of what SerpAPI
returns.

## 6. Where we'd spend more if this scaled up

If this system needed to support many more workers or much higher
traffic, the next cost/latency levers (not yet implemented, listed here so
the trade-off is explicit) would be:
- Cache repeated `serp_search` queries (same query within a session) to
  avoid duplicate paid API calls.
- Swap the keyword-based supervisor for a cheap classifier model only
  once query volume/ambiguity justifies the added latency.
- Stream the final LLM response back to the user instead of blocking on
  the full completion, to reduce *perceived* latency even though total
  token cost is unchanged.
