from mcp.server.fastmcp import FastMCP
from agent.supervisor import SupervisorAgent

supervisor = SupervisorAgent()


def register_tools(mcp: FastMCP):

    @mcp.tool()
    def research(query: str) -> str:
        """
        Routes the query through the Supervisor Agent.
        """
        return supervisor.route(query)