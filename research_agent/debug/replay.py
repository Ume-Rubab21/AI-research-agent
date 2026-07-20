"""
Agent debugging helper.

Merges logs/agent_trace.log (supervisor/worker routing decisions) and
logs/tool_calls.log (individual tool invocations) into one chronological
timeline, so a failed run can be replayed and the failure point isolated
without re-running the agent.

Usage:
    python -m debug.replay
    python -m debug.replay --last 20        # only show the last 20 events
    python -m debug.replay --component SearchWorker
"""

import argparse
import re
from pathlib import Path

TRACE_LOG = Path("logs/agent_trace.log")
TOOL_LOG = Path("logs/tool_calls.log")

TRACE_LINE = re.compile(r"^\[(?P<ts>[\d\-: ]+)\]\s\[(?P<component>[^\]]+)\]\s(?P<message>.*)$")


def parse_trace_log(path: Path):
    events = []
    if not path.exists():
        return events
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = TRACE_LINE.match(line)
        if m:
            events.append({
                "timestamp": m.group("ts"),
                "component": m.group("component"),
                "message": m.group("message"),
                "kind": "trace",
            })
    return events


def parse_tool_log(path: Path):
    """
    tool_calls.log is written as repeated blocks of:
      ============================================================
      Timestamp : ...
      Tool Name : ...
      Input     : ...
      Status    : ...
      ============================================================
    """
    events = []
    if not path.exists():
        return events

    text = path.read_text(encoding="utf-8", errors="ignore")
    blocks = text.split("=" * 60)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        fields = {}
        for line in block.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                fields[key.strip().lower()] = value.strip()

        if "timestamp" in fields and "tool name" in fields:
            events.append({
                "timestamp": fields.get("timestamp", ""),
                "component": fields.get("tool name", "unknown_tool"),
                "message": f"input={fields.get('input', '')} status={fields.get('status', '')}",
                "kind": "tool_call",
            })

    return events


def replay(component_filter: str | None = None, last: int | None = None):
    events = parse_trace_log(TRACE_LOG) + parse_tool_log(TOOL_LOG)
    events.sort(key=lambda e: e["timestamp"])

    if component_filter:
        events = [e for e in events if component_filter.lower() in e["component"].lower()]

    if last:
        events = events[-last:]

    if not events:
        print("No log events found. Run the agent (main.py, client/client.py, "
              "or the MCP server) at least once first.")
        return

    print("=" * 70)
    print(f"REPLAY - {len(events)} event(s)")
    print("=" * 70)

    for e in events:
        tag = "TOOL " if e["kind"] == "tool_call" else "TRACE"
        status = ""
        if "status=FAILED" in e["message"]:
            status = "  <-- FAILURE POINT"
        print(f"[{e['timestamp']}] [{tag}] [{e['component']}] {e['message']}{status}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replay agent trace + tool call logs.")
    parser.add_argument("--component", help="Only show events from this component/tool", default=None)
    parser.add_argument("--last", type=int, help="Only show the last N events", default=None)
    args = parser.parse_args()

    replay(component_filter=args.component, last=args.last)
