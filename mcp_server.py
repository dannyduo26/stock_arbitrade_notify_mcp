'''
Author: duyulin@kingsoft.com
Date: 2025-11-24 18:05:08
LastEditors: duyulin@kingsoft.com
LastEditTime: 2025-12-05 16:52:41
'''
import os
from typing import Any, Dict, List
from fastmcp import FastMCP
import httpx
import jisilu_mcp_server as j
import wechat_server as w

# 初始化 MCP 服务器
mcp = FastMCP("arbitrage-suite")

@mcp.tool(description="获取QDII溢价套利候选列表")
def fetch_qdii_candidates(threshold: float = 2.0) -> str:
    """
    获取QDII溢价套利候选列表

    Args:
        threshold: 溢价率阈值，默认为2.0%
    """
    import json
    result = j.qdii_candidates(threshold)
    return json.dumps(result, ensure_ascii=False)

@mcp.tool(description="发送微信通知")
async def send_wechat(title: str, desp: str) -> str:
    """
    发送微信通知

    Args:
        title: 通知的标题
        desp: 通知的详细内容
    """
    import json
    result = await w.send_wechat(title, desp)
    return json.dumps(result, ensure_ascii=False)

if __name__ == "__main__":
    # 获取端口，默认使用 4567
    port = int(os.getenv("PORT", 4567))
    
    # 以 SSE 模式启动服务器，使其支持 HTTP 远程调用
    mcp.run(
        transport="sse", 
        host="0.0.0.0", 
        port=port
    )