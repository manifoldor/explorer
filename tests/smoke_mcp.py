"""Local MCP handshake/tool-discovery smoke test; no network call."""
import asyncio
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server = str(Path(__file__).resolve().parents[1] / 'explorer.py')
    async with stdio_client(StdioServerParameters(command=sys.executable, args=[server])) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            initialized = await session.initialize()
            result = await session.list_tools()
            assert initialized.serverInfo.name == 'explorer'
            assert [tool.name for tool in result.tools] == ['github_trending_top10']
            print('PASS: explorer MCP initialize + tools/list')


asyncio.run(main())
