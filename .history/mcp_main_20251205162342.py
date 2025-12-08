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

@mcp.tool(description="获取QDII溢价套利候选列表")
def fetch_qdii_candidates(threshold: float = 2.0) -> List[Dict[str, Any]]:
    """
    获取QDII溢价套利候选列表

    Args:
        threshold: 溢价率阈值，默认为2.0%
    """
    return j.qdii_candidates(threshold)

@mcp.tool(description="发送微信通知")
async def send_wechat(title: str, desp: str) -> dict[str, Any]:
    """
    发送微信通知

    Args:
        title: 通知的标题
        desp: 通知的详细内容
    """
    return await w.send_wechat(title, desp)

if __name__ == "__main__":
    mcp.run(transport="stdio")