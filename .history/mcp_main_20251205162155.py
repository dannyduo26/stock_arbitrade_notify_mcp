'''
Author: duyulin@kingsoft.com
Date: 2025-11-24 18:05:08
LastEditors: duyulin@kingsoft.com
LastEditTime: 2025-12-05 16:21:45
FilePath: \stock_arbitrage\mcp_main.py
Description: 

'''
from typing import Any, Dict, List
from mcp.server import FastMCP
import httpx
import jisilu_mcp_server as j
import wechat_server as w

mcp = FastMCP("arbitrage-suite", json_response=True)

@mcp.tool()
def fetch_qdii_candidates(threshold: float = 2.0) -> List[Dict[str, Any]]:
    return j.qdii_candidates(threshold)

@mcp.tool()
async def send_wechat(title: str, desp: str) -> dict[str, Any]:
    return await w.send_wechat(title, desp)

if __name__ == "__main__":
    mcp.run(transport="stdio")