# MCP Arbitrage Suite

基于 MCP (Model Context Protocol) 的 QDII 溢价套利和微信通知服务套件。

## 📖 项目简介

本项目提供了一个基于 HTTP 传输的 MCP 服务器，集成了以下功能：

- **QDII 溢价套利**：从集思录抓取 QDII 基金数据，筛选满足溢价条件的套利机会
- **微信通知**：通过 Server 酱发送微信消息通知

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置文件

创建 `config.json` 文件，填入必要的配置信息：

```json
{
  "deepseek_base_url": "https://api.deepseek.com",
  "SCT_KEY": "你的Server酱Key",
  "deepseek_api_key": "你的DeepSeek API Key"
}
```

**配置说明：**

- `SCT_KEY`: Server 酱的推送 Key，用于发送微信通知（在 [Server 酱官网](https://sct.ftqq.com/) 获取）
- `deepseek_api_key`: DeepSeek API 密钥（如需使用 AI 功能）
- `deepseek_base_url`: DeepSeek API 服务地址

### 启动 MCP 服务器

```bash
python mcp_server.py
```

服务器将在 `http://127.0.0.1:4096` 启动，使用 HTTP 传输方式。

## 🔧 可用工具

### 1. fetch_qdii_candidates

获取 QDII 溢价套利候选列表。

**参数：**

- `threshold` (float, optional): 溢价率阈值，默认为 2.0%

**返回：**
返回满足以下条件的 QDII 基金列表：

- T-1 溢价率 > threshold
- 申购状态不是"暂停申购"或"开放申购"（通常是"限额申购"）

**示例：**

```python
# 获取溢价率大于2%的基金
candidates = fetch_qdii_candidates(threshold=2.0)
```

**返回数据格式：**

```json
[
  {
    "代码": "159920",
    "名称": "恒生ETF",
    "T-1溢价率": 2.5,
    "申购状态": "限额申购"
  }
]
```

### 2. send_wechat

发送微信通知消息。

**参数：**

- `title` (str, required): 通知的标题
- `desp` (str, required): 通知的详细内容

**示例：**

```python
send_wechat(
    title="QDII套利提醒",
    desp="发现3只满足条件的套利基金"
)
```

## 📁 项目结构

```
mcp/
├── README.md                    # 项目说明文档
├── requirements.txt             # Python依赖列表
├── config.json                  # 配置文件（需自行创建）
├── mcp_http_config.json         # MCP客户端HTTP配置示例
├── mcp_server.py                # MCP服务器主程序（HTTP传输）
├── jisilu_mcp_server.py         # 集思录数据抓取模块
├── wechat_server.py             # 微信通知模块
├── mcp_client.py                # MCP客户端示例
├── deepseek_client.py           # DeepSeek AI客户端
└── test_deepseek.py             # 测试脚本
```

## 💻 使用示例

### 基本调用示例

```python
import requests

MCP_BASE = "http://127.0.0.1:4096"

# 调用QDII候选工具
def call_mcp_tool(tool_name: str, params: dict = None):
    payload = {"tool": tool_name, "params": params or {}}
    res = requests.post(f"{MCP_BASE}/call", json=payload, timeout=10)
    res.raise_for_status()
    return res.json()

# 获取溢价率≥3%的基金
candidates = call_mcp_tool("fetch_qdii_candidates", {"threshold": 3.0})
print(candidates)

# 发送微信通知
result = call_mcp_tool("send_wechat", {
    "title": "套利提醒",
    "desp": f"发现 {len(candidates)} 只满足条件的基金"
})
print(result)
```

### 使用配置文件

项目提供了 `mcp_http_config.json` 配置文件示例，您可以在支持 MCP 协议的客户端中使用：

```json
{
  "mcpServers": {
    "arbitrage-suite": {
      "type": "http",
      "url": "http://127.0.0.1:4096",
      "description": "QDII溢价套利和微信通知服务"
    }
  }
}
```

## 🔍 数据来源

QDII 数据从以下来源抓取（按优先级）：

1. 集思录 API 接口（优先）
2. AKShare 数据接口（备用）

## ⚙️ 技术栈

- **MCP 框架**: FastMCP - 快速构建 MCP 服务器
- **HTTP 客户端**: httpx - 异步 HTTP 请求
- **数据解析**: BeautifulSoup4 + lxml
- **金融数据**: AKShare
- **AI 集成**: OpenAI SDK（兼容 DeepSeek）

## 📝 依赖说明

```txt
httpx>=0.28.1           # HTTP客户端
beautifulsoup4>=4.14.2  # HTML解析
lxml>=6.0.2             # XML/HTML处理
akshare>=1.17.87        # 金融数据接口
mcp>=1.21.2             # MCP协议框架
```

## 🛠️ 开发说明

### MCP 传输方式

本项目使用 **HTTP 传输方式**（而非 SSE）：

```python
# mcp_server.py
mcp.run(transport="http")  # 使用HTTP传输方式
```

### 扩展新工具

在 `mcp_server.py` 中添加新的 MCP 工具：

```python
@mcp.tool(description="工具描述")
def your_tool_name(param1: str, param2: int) -> dict:
    """
    工具说明文档

    Args:
        param1: 参数1说明
        param2: 参数2说明
    """
    # 实现逻辑
    return {"result": "success"}
```

## 📄 许可证

本项目遵循 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## ⚠️ 注意事项

1. **配置安全**：请勿将 `config.json` 提交到版本控制系统，注意保护 API 密钥
2. **频率限制**：抓取集思录数据时请注意访问频率，避免被封 IP
3. **Server 酱额度**：免费版 Server 酱有推送次数限制，请合理使用
4. **网络连接**：首次运行需要下载数据，请确保网络连接稳定

## 📚 相关文档

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [Server 酱文档](https://sct.ftqq.com/sendkey)
- [集思录 QDII 页面](https://www.jisilu.cn/data/qdii/)
- [AKShare 文档](https://akshare.akfamily.xyz/)
