from langchain.agents import create_agent
from langchain_groq import ChatGroq

from tools.serp_search import serp_search
from plugins.txt_reader import read_txt_file
from plugins.pdf_reader import read_pdf_file


def build_agent():
    """
    Create and configure the AI Research Agent.
    """

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        # A small non-zero temperature is used (instead of 0) so that if the
        # model ever emits a malformed tool call (a known, documented
        # intermittent issue with Groq's Llama models -- see
        # https://github.com/langchain-ai/langchain/issues/31459), a retry
        # actually has a chance to produce a different, well-formed
        # generation instead of deterministically repeating the same
        # failure every time.
        temperature=0.2,
    )

    agent = create_agent(
        model=llm,
        tools=[serp_search, read_txt_file, read_pdf_file],
        system_prompt="""
You are an AI Research Assistant.

Rules:

1. If the user asks about a text file, use the TXT reader tool.
2. If the user asks about a PDF file, use the PDF reader tool.
3. If the user asks for current information, latest versions, news, or web facts, use the search tool.
4. For simple math or general knowledge that does not require current information, answer directly.
5. Never expose raw search results.
6. Summarize information clearly and accurately.
7. Only answer what the user is currently asking. Do not repeat or restate
   information from earlier in the conversation unless the user specifically
   asks about it again.
8. If the user shares a personal fact (name, profession, interests), remember
   it for the session and recall it directly from memory when asked, without
   calling any tool.
""",
    )

    return agent