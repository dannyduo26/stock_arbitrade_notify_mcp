import argparse
import json
import os
from pathlib import Path
from typing import Any
import httpx


def _load_api_key() -> str | None:
    cfg_path = Path(__file__).parent / "config.json"
    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
            key = data.get("deepseek-api-key")
            if isinstance(key, str) and key:
                return key
        except Exception:
            pass
    env_key = os.getenv("DEEPSEEK_API_KEY")
    if env_key:
        return env_key
    return None


def chat(prompt: str, model: str = "deepseek-chat", system: str | None = None, max_tokens: int | None = None) -> dict[str, Any]:
    api_key = _load_api_key()
    if not api_key:
        raise RuntimeError("Missing deepseek-api-key in config.json or DEEPSEEK_API_KEY env")
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload: dict[str, Any] = {"model": model, "messages": messages}
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    with httpx.Client(timeout=60) as client:
        resp = client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="deepseek_client")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--system")
    parser.add_argument("--max-tokens", type=int)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _dry_run_output(prompt: str, model: str, system: str | None) -> dict[str, Any]:
    has_key = _load_api_key() is not None
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return {
        "has_key": has_key,
        "url": "https://api.deepseek.com/v1/chat/completions",
        "payload": {"model": model, "messages": messages},
    }


if __name__ == "__main__":
    args = _parse_args()
    if args.dry_run:
        print(json.dumps(_dry_run_output(args.prompt, args.model, args.system), ensure_ascii=False))
    else:
        data = chat(args.prompt, args.model, args.system, args.max_tokens)
        content: str = ""
        try:
            content = str(data.get("choices", [{}])[0].get("message", {}).get("content", ""))
        except Exception:
            content = ""
        print(json.dumps({"content": content, "raw": data}, ensure_ascii=False))