import sys
import json
import re
import time
from typing import List, Dict, Any

try:
    import httpx  # type: ignore
except Exception:
    httpx = None  # type: ignore

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:
    BeautifulSoup = None  # type: ignore


try:
    from mcp.server.fastmcp import FastMCP  # type: ignore
except Exception:
    FastMCP = None  # type: ignore


URL = "https://www.jisilu.cn/data/qdii/#qdiie"


def _to_float_percent(s: str) -> float:
    # 将百分数字符串转为浮点数（去掉%和+号）
    s = s.strip().replace("%", "").replace("+", "")
    try:
        return float(s)
    except Exception:
        return float("nan")


def _fetch_html(url: str) -> str:
    # 简单HTTP抓取，优先使用httpx，失败时回退到urllib
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Referer": "https://www.jisilu.cn/data/qdii/",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    if httpx is not None:
        with httpx.Client(timeout=20) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text
    import urllib.request

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def _parse_with_bs4(html: str) -> List[Dict[str, Any]]:
    # 使用BeautifulSoup解析表格，提取 T-1溢价率 与 申购状态 等字段
    try:
        from lxml import html as lxml_html  # type: ignore
    except Exception:
        return []
    try:
        tree = lxml_html.fromstring(html)
    except Exception:
        return []
    nodes = tree.xpath('//td[@data-name="apply_status"]/text()')
    result: List[Dict[str, Any]] = []
    for txt in nodes:
        s = str(txt).strip()
        if s:
            result.append({"申购状态": s})
    return result


def _parse_with_regex(html: str) -> List[Dict[str, Any]]:
    # 当表格解析失败时，使用正则从纯文本回退提取核心字段
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    chunks = re.split(r"(?=\b\d{6}\b)", text)
    result: List[Dict[str, Any]] = []
    for chunk in chunks:
        m_code = re.search(r"\b(\d{6})\b", chunk)
        if not m_code:
            continue
        code = m_code.group(1)
        m_name = re.search(r"\b\d{6}\b\s*([^\d%\-]{2,}?)\s", chunk)
        name = m_name.group(1).strip() if m_name else ""
        m_t1 = re.search(r"T-1溢价率\s*([+\-]?[\d\.]+)%", chunk)
        t1 = m_t1.group(1) + "%" if m_t1 else ""
        m_sub = re.search(r"申购状态\s*([\u4e00-\u9fffA-Za-z0-9%]+)", chunk)
        sub = m_sub.group(1) if m_sub else ""
        if t1 or sub:
            result.append({"代码": code, "名称": name, "T-1溢价率": t1, "申购状态": sub})
    return result


def _fetch_api_rows() -> List[Dict[str, Any]]:
    url = "https://www.jisilu.cn/data/qdii/qdii_list/E"
    params = {
        "___jsl": f"LST___t={int(time.time()*1000)}",
        "only_lof": "y",
        "only_etf": "y",
        "rp": "200",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Referer": "https://www.jisilu.cn/data/qdii/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    try:
        if httpx is not None:
            resp = httpx.get(url, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        else:
            import urllib.parse
            import urllib.request
            q = urllib.parse.urlencode(params)
            req = urllib.request.Request(url + "?" + q, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as f:
                data = json.loads(f.read().decode("utf-8", errors="ignore"))
    except Exception:
        return []
    out: List[Dict[str, Any]] = []
    for row in data.get("rows", []):
        cell = row.get("cell", {})
        out.append({
            "代码": str(cell.get("fund_id", "")),
            "名称": str(cell.get("fund_nm", "")),
            "T-1溢价率": str(cell.get("discount_rt", "")),
            "申购状态": str(cell.get("apply_status", "")),
        })
    return out

def _fetch_data() -> List[Dict[str, Any]]:
    # 数据源优先：AKShare结构化接口；如不可用，回退到网页解析
    try:
        import akshare as ak  # type: ignore
        datasets: List[Any] = []
        try:
            if hasattr(ak, "qdii_e_index_jsl"):
                datasets.append(ak.qdii_e_index_jsl())
        except Exception:
            pass
        try:
            if hasattr(ak, "qdii_e_comm_jsl"):
                datasets.append(ak.qdii_e_comm_jsl())
        except Exception:
            pass
        print(datasets)
        rows: List[Dict[str, Any]] = []
        for df in datasets:
            try:
                for _, r in df.iterrows():
                    rows.append({
                        "代码": str(r.get("代码", "")),
                        "名称": str(r.get("名称", "")),
                        "T-1溢价率": str(r.get("T-1溢价率", r.get("T-1 溢价率", ""))),
                        "申购状态": str(r.get("申购状态", "")),
                    })
            except Exception:
                continue
        if rows:
            api_rows = _fetch_api_rows()
            status_map: Dict[str, str] = {}
            premium_map: Dict[str, str] = {}
            for ar in api_rows:
                c = str(ar.get("代码", ""))
                if c:
                    status_map[c] = str(ar.get("申购状态", ""))
                    premium_map[c] = str(ar.get("T-1溢价率", ""))
            for r in rows:
                c = str(r.get("代码", ""))
                if c:
                    if not str(r.get("T-1溢价率", "")):
                        r["T-1溢价率"] = premium_map.get(c, r.get("T-1溢价率", ""))
                    r["申购状态"] = status_map.get(c, r.get("申购状态", ""))
            return rows
    except Exception:
        pass
    return _fetch_api_rows()


def qdii_candidates(threshold: float = 2.0) -> List[Dict[str, Any]]:
    # 过滤逻辑：T-1溢价率 > threshold 且 申购状态 ≠ "暂停申购"
    rows = _fetch_data()
    out: List[Dict[str, Any]] = []
    for r in rows:
        p = _to_float_percent(str(r.get("T-1溢价率", "")))
        status = str(r.get("申购状态", ""))
        if p == p and p > threshold and status != "暂停申购":
            out.append({
                "代码": r.get("代码", ""),
                "名称": r.get("名称", ""),
                "T-1溢价率": p,
                "申购状态": status,
            })
    return out


def qdii_limit_codes(threshold: float = 2.0) -> List[str]:
    rows = _fetch_data()
    codes: List[str] = []
    for r in rows:
        p = _to_float_percent(str(r.get("T-1溢价率", "")))
        status = str(r.get("申购状态", ""))
        if p == p and p > threshold and status.startswith("限"):
            c = str(r.get("代码", ""))
            if c:
                codes.append(c)
    return codes

mcp = FastMCP("jisilu-qdii") if FastMCP is not None else None

if mcp is not None:
    # MCP工具：返回满足条件的QDII基金列表
    @mcp.tool()
    def fetch_qdii_candidates(threshold: float = 2.0) -> List[Dict[str, Any]]:
        return qdii_candidates(threshold)

    @mcp.tool()
    def fetch_qdii_limit_codes(threshold: float = 2.0) -> List[str]:
        return qdii_limit_codes(threshold)


if __name__ == "__main__":
    # 支持快速本地测试与MCP服务运行
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        res = qdii_candidates(2.0)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif mcp is not None:
        mcp.run()
    else:
        res = qdii_candidates(2.0)
        print(json.dumps(res, ensure_ascii=False, indent=2))
# MCP服务器：抓取集思录QDII页面数据，筛选满足溢价与申购条件的基金
# 提供工具 fetch_qdii_candidates 供外部通过MCP调用