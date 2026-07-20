from datetime import datetime
import os


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "agent_trace.log")


class Tracer:

    @staticmethod
    def log(component: str, message: str):

        os.makedirs(LOG_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_line = f"[{timestamp}] [{component}] {message}\n"

        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(log_line)

        print(log_line, end="")