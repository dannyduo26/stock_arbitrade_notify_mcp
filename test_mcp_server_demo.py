import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test_remote_mcp():
    # 替换为你的服务器实际 IP 或域名
    # 如果你在本地测试，使用 http://localhost:8080/sse
    server_url = "http://localhost:8080/sse"
    
    print(f"正在连接到 MCP 服务器: {server_url}...")
    
    try:
        async with sse_client(server_url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # 1. 初始化会话
                await session.initialize()
                print("✅ 已成功建立连接并初始化。")

                # 2. 列出所有可用的工具
                tools = await session.list_tools()
                print(f"\n[可用工具]: {[tool.name for tool in tools.tools]}")

                # 3. 测试调用 'add_numbers' 工具
                print("\n正在测试 'add_numbers' 工具...")
                result = await session.call_tool("add_numbers", arguments={"a": 15, "b": 27})
                
                # 解析返回结果（假设返回的是文本）
                if result.content:
                    print(f"👉 计算结果: {result.content[0].text}")
                
                # 4. 测试读取资源
                print("\n正在测试 'config://env' 资源...")
                resource = await session.read_resource("config://env")
                print(f"👉 资源内容: {resource.contents[0].text}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_remote_mcp())