import sys
import json
import re
from typing import Any, Dict, List

import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("jisilu-qdii")


def _fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.jisilu.cn/data/qdii/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    }
    with httpx.Client(timeout=20) as client:
        r = client.get(url, headers=headers)
        r.raise_for_status()
        return r.text


def _parse_tables(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
    rows: List[Dict[str, Any]] = []
    for tbl in tables:
        headers: List[str] = []
        thead = tbl.find("thead")
        if thead:
            ths = thead.find_all("th")
            headers = [th.get_text(strip=True) for th in ths]
        if not headers:
            first_tr = tbl.find("tr")
            if first_tr:
                headers = [td.get_text(strip=True) for td in first_tr.find_all(["th", "td"])]
        if not headers:
            continue
        if "T-1溢价率" not in headers or "申购状态" not in headers:
            continue
        body_rows = tbl.find_all("tr")
        for tr in body_rows[1:]:
            tds = tr.find_all("td")
            if not tds or len(tds) < len(headers):
                continue
            data: Dict[str, Any] = {}
            for i, h in enumerate(headers):
                data[h] = tds[i].get_text(strip=True)
            rows.append(data)
    if rows:
        return rows
    text = soup.get_text(" ", strip=True)
    pattern = re.compile(r"(\d{6})\s+([^\s]+).*?T-1估值\s+([^\s]+).*?T-1溢价率\s+([\-\+]?\d+\.\d+)%.*?申购状态\s+([\u4e00-\u9fa5]+)")
    parsed: List[Dict[str, Any]] = []
    for m in pattern.finditer(text):
        parsed.append(
            {
                "代码": m.group(1),
                "名称": m.group(2),
                "T-1估值": m.group(3),
                "T-1溢价率": m.group(4) + "%",
                "申购状态": m.group(5),
            }
        )
    return parsed


def _parse_percent(pct_text: str) -> float:
    s = pct_text.strip().replace("%", "")
    try:
        return float(s)
    except Exception:
        return float("nan")


@mcp.tool
def qdii_premium_candidates(
    min_premium: float = 2.0,
    url: str = "https://www.jisilu.cn/data/qdii/#qdiie",
) -> List[Dict[str, Any]]:
    """返回T-1溢价率大于阈值且申购状态不为暂停申购的基金列表"""
    html = _fetch_html(url)
    rows = _parse_tables(html)
    result: List[Dict[str, Any]] = []
    for row in rows:
        premium_text = row.get("T-1溢价率", "")
        sub_status = row.get("申购状态", "")
        premium = _parse_percent(premium_text)
        if premium != premium:  # NaN
            continue
        if premium > min_premium and sub_status != "暂停申购":
            item = {
                "代码": row.get("代码", ""),
                "名称": row.get("名称", ""),
                "T-1溢价率": premium,
                "申购状态": sub_status,
                "T-1估值": row.get("T-1估值", ""),
                "估值日期": row.get("估值日期", ""),
            }
            result.append(item)
    return result


if __name__ == "__main__":
    if "--test" in sys.argv:
        data = qdii_premium_candidates()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        mcp.run()