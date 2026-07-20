from plugins.pdf_reader import read_pdf_file
from plugins.txt_reader import read_txt_file

from agent.builder import build_agent
from memory.session_memory import SessionMemory


agent = build_agent()
memory = SessionMemory()


def process_file(query: str) -> str:
    """
    Reads a PDF/TXT file and lets the research agent answer
    the user's request about that file.
    """

    words = query.split()

    file_path = None

    for word in words:
        if word.endswith(".pdf") or word.endswith(".txt"):
            file_path = word
            break

    if file_path is None:
        return "Please specify a PDF or TXT file."

    if file_path.endswith(".pdf"):
        file_content = read_pdf_file.invoke(file_path)
    else:
        file_content = read_txt_file.invoke(file_path)

    prompt = f"""
User Request:
{query}

File Content:
{file_content}

Answer the user's request using ONLY the file content.
"""

    memory.add_user_message(prompt)

    result = agent.invoke(
        {
            "messages": memory.get_messages()
        }
    )

    answer = result["messages"][-1].content

    memory.add_ai_message(answer)

    return answer