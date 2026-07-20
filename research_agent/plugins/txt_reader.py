from pathlib import Path

from langchain_core.tools import tool

from hooks.logger import log_tool_call


@tool
def read_txt_file(file_path: str) -> str:
    """
    Read the contents of a text (.txt) file.
    """

    try:
        path = Path(file_path)

        if not path.exists():
            log_tool_call(
                tool_name="read_txt_file",
                tool_input=file_path,
                status="FAILED"
            )
            return f"File not found: {file_path}"

        if path.suffix.lower() != ".txt":
            log_tool_call(
                tool_name="read_txt_file",
                tool_input=file_path,
                status="FAILED"
            )
            return "Only .txt files are supported."

        content = path.read_text(encoding="utf-8")

        log_tool_call(
            tool_name="read_txt_file",
            tool_input=file_path,
            status="SUCCESS"
        )

        return content

    except Exception as e:
        log_tool_call(
            tool_name="read_txt_file",
            tool_input=file_path,
            status="FAILED"
        )
        return f"Error: {e}"