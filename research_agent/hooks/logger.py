from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "tool_calls.log"


def log_tool_call(tool_name: str, tool_input: str, status: str = "SUCCESS"):
    """
    Log every tool call with a timestamp.
    """

    LOG_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write("=" * 60 + "\n")
        file.write(f"Timestamp : {timestamp}\n")
        file.write(f"Tool Name : {tool_name}\n")
        file.write(f"Input     : {tool_input}\n")
        file.write(f"Status    : {status}\n")
        file.write("=" * 60 + "\n\n")