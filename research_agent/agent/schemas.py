"""
Structured-output guardrail.

Every answer that leaves the Supervisor (and therefore the MCP `research`
tool) is passed through AgentAnswer before it reaches the user/client.
This gives us one place to enforce:
  - the answer is non-empty and within a sane length
  - raw tool/search payloads never leak to the user
  - we always know which worker produced the answer (for tracing/debugging)
"""

from typing import Literal
from pydantic import BaseModel, field_validator

MAX_ANSWER_CHARS = 4000


class AgentAnswer(BaseModel):
    answer: str
    source: Literal["search_worker", "file_worker", "search_worker+file_worker"]

    @field_validator("answer")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Agent produced an empty answer.")
        return v.strip()

    @field_validator("answer")
    @classmethod
    def not_too_long(cls, v: str) -> str:
        if len(v) > MAX_ANSWER_CHARS:
            return v[:MAX_ANSWER_CHARS].rstrip() + "... [truncated]"
        return v

    @field_validator("answer")
    @classmethod
    def no_raw_dump_markers(cls, v: str) -> str:
        # crude but effective guard against leaking raw tool payloads
        # (e.g. an unsummarized SerpAPI dict/list dump)
        suspicious_markers = ("Title: ", "{'organic_results'", "[{'title'")
        if any(v.startswith(m) for m in suspicious_markers):
            raise ValueError(
                "Agent returned an unsummarized raw tool payload instead "
                "of a natural-language answer."
            )
        return v


def validate_answer(raw_text: str, source: str) -> str:
    """
    Runs raw_text through the AgentAnswer guardrail.
    On failure, returns a safe fallback instead of raising, so a bad
    validation never crashes the agent graph.
    """
    try:
        validated = AgentAnswer(answer=raw_text, source=source)
        return validated.answer
    except Exception as e:
        return (
            "I ran into a problem producing a clean answer for that "
            f"request ({e}). Could you try rephrasing it?"
        )
