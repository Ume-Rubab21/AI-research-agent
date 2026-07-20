from mcp.server.fastmcp import FastMCP

from mcp_server.resources import register_resources
from mcp_server.tools import register_tools

mcp = FastMCP("Research Agent MCP Server")

register_resources(mcp)
register_tools(mcp)

if __name__ == "__main__":
    print("Starting Research Agent MCP Server...")
    mcp.run()          # Default = stdio