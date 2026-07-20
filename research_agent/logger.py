from datetime import datetime


def log_tool(tool_name: str, tool_input: str, tool_output: str):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs.txt", "a", encoding="utf-8") as file:

        file.write("=" * 60 + "\n")

        file.write(f"Time : {timestamp}\n\n")

        file.write(f"Tool :\n{tool_name}\n\n")

        file.write(f"Input :\n{tool_input}\n\n")

        file.write(f"Output :\n{tool_output}\n\n")

        file.write("=" * 60 + "\n\n")