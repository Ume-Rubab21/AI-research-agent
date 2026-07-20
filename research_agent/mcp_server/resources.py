from mcp.server.fastmcp import FastMCP

def register_resources(mcp: FastMCP):

    @mcp.resource("research://about")
    def about() -> str:
        return """
Research Agent v1.0

Features:
- Brave Web Search
- PDF Reader
- TXT Reader
- Memory
- MCP Integration
"""