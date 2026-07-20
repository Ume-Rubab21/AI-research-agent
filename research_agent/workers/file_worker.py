from plugins.pdf_reader import read_pdf_file
from plugins.txt_reader import read_txt_file
from tracing.tracer import Tracer


class FileWorker:

    def process(self, query: str) -> str:

        Tracer.log("FileWorker", f"Received query: {query}")

        words = query.split()

        file_path = None

        for word in words:
            if word.endswith(".pdf") or word.endswith(".txt"):
                file_path = word
                break

        if not file_path:
            return "No file specified."

        if file_path.endswith(".pdf"):
            content = read_pdf_file.invoke(file_path)
        else:
            content = read_txt_file.invoke(file_path)

        Tracer.log("FileWorker", "Finished processing")

        return content