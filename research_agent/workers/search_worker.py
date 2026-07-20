from agent.research_service import run_research
from tracing.tracer import Tracer


class SearchWorker:

    def process(self, query: str, context: str = "") -> str:

        Tracer.log("SearchWorker", f"Received query: {query}")

        if context:
            query = f"""
Context from file:

{context}

User Question:
{query}
"""

        answer = run_research(query)

        Tracer.log("SearchWorker", "Finished processing")

        return answer