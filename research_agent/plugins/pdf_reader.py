from pathlib import Path

from langchain_core.tools import tool
from pypdf import PdfReader

from hooks.logger import log_tool_call


@tool
def read_pdf_file(file_path: str) -> str:
    """
    Read text from a PDF file.
    """

    try:
        path = Path(file_path)

        if not path.exists():
            log_tool_call(
                tool_name="read_pdf_file",
                tool_input=file_path,
                status="FAILED"
            )
            return f"File not found: {file_path}"

        if path.suffix.lower() != ".pdf":
            log_tool_call(
                tool_name="read_pdf_file",
                tool_input=file_path,
                status="FAILED"
            )
            return "Only .pdf files are supported."

        reader = PdfReader(path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        log_tool_call(
            tool_name="read_pdf_file",
            tool_input=file_path,
            status="SUCCESS"
        )

        if not text.strip():
            return "The PDF contains no readable text."

        return text

    except Exception as e:
        log_tool_call(
            tool_name="read_pdf_file",
            tool_input=file_path,
            status="FAILED"
        )
        return f"Error: {e}"