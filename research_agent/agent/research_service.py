import json
import re
import time
import traceback

from agent.builder import build_agent
from memory.session_memory import SessionMemory
from tracing.tracer import Tracer
from tools.serp_search import serp_search
from plugins.txt_reader import read_txt_file
from plugins.pdf_reader import read_pdf_file

# Create one shared agent
agent = build_agent()

# Shared memory
memory = SessionMemory()

# Map of tool name -> actual tool object, used only for the self-healing
# recovery path below (never for normal operation).
_TOOLS_BY_NAME = {
    "serp_search": serp_search,
    "read_txt_file": read_txt_file,
    "read_pdf_file": read_pdf_file,
}

# Matches Groq's malformed tool-call generations, e.g.:
#   <function=serp_search[]{"query": "latest version of python"}</function>
#   <function=serp_search{"query": "latest version of python"}</function>
_MALFORMED_TOOL_CALL_PATTERN = re.compile(
    r"<function=(\w+)\[?\]?(\{.*\})\s*</?function>?",
    re.DOTALL,
)


def _try_recover_from_malformed_tool_call(error):
    """
    Groq's Llama models occasionally emit a malformed tool call (a raw
    <function=...>{...}</function> tag) instead of a properly structured
    tool call. Groq's API then rejects the whole request with a 400
    'tool_use_failed' error. This is a known, documented issue with
    Groq + Llama tool calling (see
    https://github.com/langchain-ai/langchain/issues/31459), and retrying
    with the same input often reproduces the exact same malformed output.

    Instead of just retrying and hoping, we recover directly: the raw
    (malformed) tool call is still readable inside
    error.body['error']['failed_generation']. We parse out the intended
    tool name + arguments ourselves, run the *real* tool with them, and
    return its result as the answer. This makes the pipeline self-healing
    instead of purely luck-based.

    Returns the recovered answer string, or None if recovery wasn't
    possible (e.g. this wasn't a tool_use_failed error, or the malformed
    text couldn't be parsed).
    """

    body = getattr(error, "body", None)

    if not isinstance(body, dict):
        return None

    error_info = body.get("error", {})

    if error_info.get("code") != "tool_use_failed":
        return None

    failed_generation = error_info.get("failed_generation", "")

    match = _MALFORMED_TOOL_CALL_PATTERN.search(failed_generation)

    if not match:
        return None

    tool_name = match.group(1)
    args_json = match.group(2)

    tool = _TOOLS_BY_NAME.get(tool_name)

    if tool is None:
        return None

    try:
        args = json.loads(args_json)
        tool_result = tool.invoke(args)
    except Exception:
        return None

    Tracer.log(
        "SearchWorker/recovery",
        f"Recovered malformed tool call for '{tool_name}' with args {args}"
    )

    return str(tool_result)


def run_research(query: str, max_retries: int = 5) -> str:
    """
    Runs the Research Agent with retry support, plus self-healing recovery
    for Groq's known malformed-tool-call failure mode.
    """

    memory.add_user_message(query)

    last_error = None

    for attempt in range(1, max_retries + 1):

        try:

            result = agent.invoke(
                {
                    "messages": memory.get_messages()
                }
            )

            answer = result["messages"][-1].content

            memory.add_ai_message(answer)

            return answer

        except Exception as e:

            last_error = e

            # Print the FULL traceback so the real cause (bad API key,
            # invalid model name, rate limit, network block, etc.) is
            # visible instead of being silently swallowed.
            print(f"\n[ERROR] run_research attempt {attempt}/{max_retries} failed:")
            traceback.print_exc()

            Tracer.log(
                "SearchWorker/run_research",
                f"Attempt {attempt}/{max_retries} failed: {type(e).__name__}: {e}"
            )

            recovered = _try_recover_from_malformed_tool_call(e)

            if recovered:
                memory.add_ai_message(recovered)
                Tracer.log(
                    "SearchWorker/recovery",
                    "Recovered from malformed tool call; returning tool result directly."
                )
                return recovered

            time.sleep(1)

    return (
        f"I couldn't process that request after {max_retries} attempts. "
        f"Last error: {type(last_error).__name__}: {last_error}"
    )
