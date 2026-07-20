import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from serpapi import GoogleSearch
from logger import log_tool
load_dotenv()


@tool
def web_search(query: str) -> str:
    """
    Search Google using SerpAPI.
    """

    params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERPAPI_API_KEY"),
        "num": 5
    }

    try:

        search = GoogleSearch(params)
        results = search.get_dict()

        if "organic_results" not in results:

            output = "No search results found."

            log_tool(
                "web_search",
                query,
                output
            )

            return output

        answer = []

        for result in results["organic_results"][:5]:

            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")

            answer.append(
                f"Title: {title}\n"
                f"Snippet: {snippet}\n"
                f"Link: {link}"
            )

        final_answer = "\n\n".join(answer)

        log_tool(
            "web_search",
            query,
            final_answer
        )

        return final_answer

    except Exception as e:

        log_tool(
            "web_search",
            query,
            str(e)
        )

        return str(e)