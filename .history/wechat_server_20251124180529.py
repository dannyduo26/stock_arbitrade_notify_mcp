'''
Author: duyulin@kingsoft.com
Date: 2025-11-24 17:40:27
LastEditors: duyulin@kingsoft.com
LastEditTime: 2025-11-24 17:50:18
FilePath: \send_message\wechat_server.py
Description: 

'''
from typing import Any
import argparse
import asyncio
import json
import os
from pathlib import Path
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("wechat-notify", json_response=True)


def _load_sct_key() -> str | None:
    cfg_path = Path(__file__).parent / "config.json"
    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
            key = data.get("SCT_KEY")
            if isinstance(key, str) and key:
                return key
        except Exception:
            pass
    env_key = os.getenv("SCT_KEY")
    if env_key:
        return env_key
    return None


def _build_api_url() -> str:
    key = _load_sct_key()
    if not key:
        raise RuntimeError("Missing SCT_KEY in config.json or environment")
    return f"https://sctapi.ftqq.com/{key}.send"


@mcp.tool()
async def send_wechat(title: str, desp: str) -> dict[str, Any]:
    api_url = _build_api_url()
    async with httpx.AsyncClient() as client:
        headers = {"Content-Type": "application/json"}
        payload = {"title": title, "desp": desp}
        try:
            resp = await client.post(api_url, json=payload, headers=headers, timeout=30.0)
            data: Any
            try:
                data = resp.json()
            except Exception:
                data = {"text": resp.text}
            return {"status_code": resp.status_code, "response": data}
        except Exception as e:
            return {"error": str(e)}

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="wechat_server")
    subparsers = parser.add_subparsers(dest="cmd", required=False)

    p_server = subparsers.add_parser("server")
    p_server.add_argument("--port", type=int, default=5012)

    p_send = subparsers.add_parser("send")
    p_send.add_argument("--title", required=True)
    p_send.add_argument("--desp", required=True)
    p_send.add_argument("--dry-run", action="store_true")

    return parser.parse_args()


def _run_server(port: int) -> None:
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)


async def _run_send(api_url: str, title: str, desp: str, dry_run: bool) -> None:
    if dry_run:
        key = _load_sct_key()
        url = _build_api_url() if key else "<missing key>"
        print({"api_url": url, "payload": {"title": title, "desp": desp}})
        return
    result = await send_wechat(title, desp)
    print(result)


if __name__ == "__main__":
    args = _parse_args()
    if args.cmd == "send":
        asyncio.run(_run_send("", args.title, args.desp, args.dry_run))