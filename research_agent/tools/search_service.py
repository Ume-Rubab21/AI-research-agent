import os

from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")


def search_google(query: str) -> str:
    """
    Perform a Google search using SerpAPI.
    """

    if not SERPAPI_API_KEY:
        return "SERPAPI_API_KEY not found."

    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": 5,
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        organic = results.get("organic_results", [])

        if not organic:
            return "No search results found."

        output = []

        for item in organic:
            output.append(
                f"Title: {item.get('title')}\n"
                f"Link: {item.get('link')}\n"
                f"Snippet: {item.get('snippet')}"
            )

        return "\n\n".join(output)

    except Exception as e:
        return f"Error: {e}"