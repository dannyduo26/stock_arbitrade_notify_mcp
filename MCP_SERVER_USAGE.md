# MCP 服务启动与调用

## 启动
- 启动整合服务：
  ```bash
  python mcp_main.py
  ```
- 默认地址：`http://localhost:5011/mcp`

## 可用工具
- `fetch_qdii_candidates(threshold: float = 2.0)`：返回满足条件的基金明细列表
- `fetch_qdii_limit_codes(threshold: float = 2.0)`：返回满足条件的基金代码列表
- `send_wechat(title: str, desp: str)`：发送微信消息（需配置 `SCT_KEY` 于 `config.json` 或环境变量）

## 调用
- 在支持 MCP 的客户端/IDE 中，连接 `http://localhost:5011/mcp`，选择工具并传入参数。
- 入参示例：
  - `fetch_qdii_candidates`: `{ "threshold": 2.0 }`
  - `send_wechat`: `{ "title": "标题", "desp": "内容" }`