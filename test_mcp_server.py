"""
MCP服务器测试脚本
测试fetch_qdii_candidates和send_wechat工具
使用 SSE 传输方式
"""
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test_arbitrage_mcp():
    # MCP 服务器地址
    server_url = "http://localhost:4567/sse"
    
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

                # 3. 测试调用 'fetch_qdii_candidates' 工具
                print("\n" + "=" * 50)
                print("测试1: 获取QDII溢价套利候选")
                print("=" * 50)
                
                # 测试不同的阈值
                thresholds = [1.0, 2.0, 3.0]
                
                for threshold in thresholds:
                    print(f"\n正在获取溢价率 >= {threshold}% 的基金...")
                    result = await session.call_tool(
                        "fetch_qdii_candidates", 
                        arguments={"threshold": threshold}
                    )
                    
                    # 解析返回结果
                    if result.content:
                        import json
                        candidates_text = result.content[0].text
                        
                        # 尝试解析JSON
                        try:
                            candidates = json.loads(candidates_text)
                            print(f"[OK] 成功获取 {len(candidates)} 只基金")
                            
                            # 显示前3只基金
                            if candidates and isinstance(candidates, list):
                                print(f"\n前{min(3, len(candidates))}只基金:")
                                for i, fund in enumerate(candidates[:3], 1):
                                    if isinstance(fund, dict):
                                        print(f"  {i}. {fund.get('名称', 'N/A')} ({fund.get('代码', 'N/A')})")
                                        print(f"     溢价率: {fund.get('T-1溢价率', 'N/A')}%")
                                        print(f"     申购状态: {fund.get('申购状态', 'N/A')}")
                            else:
                                print(f"  暂无满足条件的基金")
                        except json.JSONDecodeError as e:
                            print(f"[ERROR] JSON解析失败: {e}")
                            print(f"[DEBUG] 返回内容: {candidates_text[:200]}")
                
                # 4. 测试微信通知工具（可选）
                print("\n" + "=" * 50)
                print("测试2: 发送微信通知（可选）")
                print("=" * 50)
                
                # 询问是否测试微信通知
                print("\n注意: 这将发送真实的微信通知。")
                user_input = input("是否测试微信通知功能? (y/N): ").strip().lower()
                
                if user_input == 'y':
                    print("\n发送测试通知...")
                    result = await session.call_tool(
                        "send_wechat",
                        arguments={
                            "title": "MCP Server 测试",
                            "desp": "这是来自MCP服务器的测试通知。\n\n服务器运行正常！"
                        }
                    )
                    
                    if result.content:
                        response_text = result.content[0].text
                        print(f"[OK] 通知发送成功")
                        print(f"  响应: {response_text}")
                else:
                    print("跳过微信通知测试")

                print("\n" + "=" * 50)
                print("测试完成！")
                print("=" * 50)

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_arbitrage_mcp())
