from langchain_core.tools import tool

from hooks.logger import log_tool_call
from tools.search_service import search_google


@tool
def serp_search(query: str) -> str:
    """
    Search Google using SerpAPI.
    """

    try:
        result = search_google(query)

        log_tool_call(
            tool_name="serp_search",
            tool_input=query,
            status="SUCCESS"
        )

        return result

    except Exception as e:

        log_tool_call(
            tool_name="serp_search",
            tool_input=query,
            status="FAILED"
        )

        return str(e)