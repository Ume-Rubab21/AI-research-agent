import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_server.server"],
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            print("=" * 60)
            print("        MCP Research Client")
            print("=" * 60)

            while True:

                query = input("\nYou : ")

                if query.lower() == "exit":
                    print("\nGoodbye!")
                    break

                print("\nThinking...\n")

                result = await session.call_tool(
                    "research",
                    {
                        "query": query
                    }
                )

                print("Assistant :", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())