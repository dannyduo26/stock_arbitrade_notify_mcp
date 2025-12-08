from typing import Any, Dict, List
from mcp.server import FastMCP
import jisilu_mcp_server as j
import wechat_server as w

mcp = FastMCP("arbitrage-suite", json_response=True)

@mcp.tool()
def fetch_qdii_candidates(threshold: float = 2.0) -> List[Dict[str, Any]]:
    return j.qdii_candidates(threshold)

@mcp.tool()
async def send_wechat(title: str, desp: str) -> dict[str, Any]:
    return await w.send_wechat(title, desp)

@app.tool()
async def web_search(query: str) -> str:
    """
    搜索互联网内容

    Args:
        query: 要搜索内容

    Returns:
        搜索结果的总结
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://open.bigmodel.cn/api/paas/v4/tools',
            headers={'Authorization': '换成你自己的API KEY'},
            json={
                'tool': 'web-search-pro',
                'messages': [
                    {'role': 'user', 'content': query}
                ],
                'stream': False
            }
        )

        res_data = []
        for choice in response.json()['choices']:
            for message in choice['message']['tool_calls']:
                search_results = message.get('search_result')
                if not search_results:
                    continue
                for result in search_results:
                    res_data.append(result['content'])

        return '\n\n\n'.join(res_data)

if __name__ == "__main__":
    mcp.run(transport="stdio")