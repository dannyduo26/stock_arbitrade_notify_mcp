'''
Author: duyulin@kingsoft.com
Date: 2025-11-25 10:06:07
LastEditors: duyulin@kingsoft.com
LastEditTime: 2025-11-25 10:06:20
FilePath: \stock_arbitrage\mcp_client.py
Description: 

'''
import asyncio

from fastmcp import Client


async def main():
    async with Client("http://127.0.0.1:8000/mcp-server/mcp") as client:
        result = await client.call_tool("add", {"a": 1, "b": 2})
        print(result)


if __name__ == "__main__":
    asyncio.run(main())