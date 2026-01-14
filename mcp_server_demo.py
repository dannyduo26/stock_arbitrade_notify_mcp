import os
import asyncio
from fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("My Remote Server")

# 示例工具：加法运算
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """将两个数字相加。"""
    return a + b

# 示例资源：读取服务器环境变量
@mcp.resource("config://env")
def get_env() -> str:
    """返回服务器的关键环境变量（演示资源读取）。"""
    return f"Deployment Environment: {os.getenv('ENV_TYPE', 'production')}"

if __name__ == "__main__":
    # 获取端口，生产环境通常由云服务商通过 PORT 环境变量提供
    port = int(os.getenv("PORT", 8080))
    
    # 以 SSE 模式启动服务器，使其支持 HTTP 远程调用
    mcp.run(
        transport="sse", 
        host="0.0.0.0", 
        port=port
    )