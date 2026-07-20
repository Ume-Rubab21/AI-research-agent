from workers.search_worker import SearchWorker
from workers.file_worker import FileWorker
from tracing.tracer import Tracer


class SupervisorAgent:

    def __init__(self):
        self.search_worker = SearchWorker()
        self.file_worker = FileWorker()

    def route(self, query: str) -> str:

        Tracer.log("Supervisor", f"Received query: {query}")

        lower = query.lower()

        needs_file = any(x in lower for x in [
            ".pdf",
            ".txt",
            "read",
            "file"
        ])

        needs_search = any(x in lower for x in [
            "latest",
            "current",
            "web",
            "today",
            "newest",
            "recent"
        ])

        # ---------- BOTH WORKERS ----------

        if needs_file and needs_search:

            Tracer.log("Supervisor", "Routing to FileWorker + SearchWorker")

            file_content = self.file_worker.process(query)

            return self.search_worker.process(
                query,
                context=file_content
            )

        # ---------- FILE ----------

        if needs_file:

            Tracer.log("Supervisor", "Routing to FileWorker")

            file_content = self.file_worker.process(query)

            return self.search_worker.process(
                f"Summarize this file in response to the user's request.",
                context=file_content
            )

        # ---------- SEARCH ----------

        Tracer.log("Supervisor", "Routing to SearchWorker")

        return self.search_worker.process(query)