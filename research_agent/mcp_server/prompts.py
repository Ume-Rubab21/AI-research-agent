from mcp.server.fastmcp import FastMCP


def register_prompts(mcp: FastMCP):
    """
    Registers reusable prompt templates that an MCP client (Claude Code,
    Cursor, custom client, etc.) can pull and fill in, instead of the
    user having to hand-write the wording every time.
    """

    @mcp.prompt()
    def research_query(topic: str) -> str:
        """
        Prompt template for asking the research agent to investigate a topic
        using both file context (if relevant) and live web search.
        """
        return (
            f"Research the topic: {topic}\n\n"
            "If a local file (.txt or .pdf) is relevant, read it first. "
            "Then, if the topic requires current/latest information, use "
            "web search. Combine both into a single, clearly summarized "
            "answer. Do not expose raw search results or file dumps."
        )

    @mcp.prompt()
    def summarize_file(file_path: str) -> str:
        """
        Prompt template for summarizing a specific local file.
        """
        return (
            f"Read the file at '{file_path}' and produce a concise, "
            "accurate summary of its contents. Only use information "
            "found in the file itself."
        )
