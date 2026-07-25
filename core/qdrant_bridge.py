"""
core/qdrant_bridge.py — 巨作 ↔ 熔知 数据桥（只读）

【设计说明 · AI 设计决策，非用户指令，待确认】
探查发现：熔知（Citrinitas）当前没有可用的 HTTP 读取端点
（/api/documents/search 实测返回 NiceGUI 404 页面）。但它的数据完整落在
共享的 Qdrant 向量库（collection = athanor_v1，地址见下）。

因此周看板采用「直读共享数据层 Qdrant」而非「调熔知 API」：
  - 零新依赖（用标准库 urllib，不引入 qdrant_client）；
  - 保持「五器独立」：巨作不 import 熔知代码、不依赖熔知运行时，
    只读取共享存储（与跨器读同一份数据），符合数据集成而非代码耦合原则；
  - 地址 / 集合名可由巨作 .env 的 QDRANT_URL / QDRANT_COLLECTION 覆盖，
    默认值复用熔知当前值。

这是 MVP 路径；等熔知补齐官方读取 API 后，可平滑切换到 API 调用。
"""

import json
import os
import urllib.request
from datetime import datetime, timedelta

# 默认值与熔知当前配置保持一致；可在巨作 .env 覆盖
QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333").rstrip("/")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "athanor_v1")


def _post(path: str, body: dict, timeout: int = 8):
    """对 Qdrant REST 发 POST，返回解析后的 dict。失败时抛异常由调用方处理。"""
    url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def qdrant_reachable() -> bool:
    """探测 Qdrant 是否在线（用于区分「知识库空」与「连不上」）。"""
    try:
        url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}"
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def scroll_payloads(limit: int = 200) -> list:
    """翻页拉取集合内全部文档 payload，按 created_at 降序返回。

    返回 list[dict]，每个元素是熔知写入的文档 payload 字段
    （doc_id / title / source / domain / content_preview / created_at ...）。
    """
    out = []
    offset = None
    while True:
        body = {"with_payload": True, "with_vector": False, "limit": limit}
        if offset is not None:
            body["offset"] = offset
        try:
            res = _post("points/scroll", body)
        except Exception:
            break
        pts = (res.get("result") or {}).get("points") or []
        if not pts:
            break
        for p in pts:
            out.append(p.get("payload") or {})
        if len(pts) < limit:
            break
        # 兼容新版 next_page_offset / 旧版 offset 两种分页标记
        nxt = (res.get("result") or {}).get("next_page_offset")
        offset = nxt if nxt is not None else pts[-1].get("id")
    out.sort(key=_parse_dt_or_min, reverse=True)
    return out


def _parse_dt(s: str):
    """把 created_at 解析成朴素 datetime（丢弃时区，按本地时间比较，MVP 简化）。"""
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


def _parse_dt_or_min(s: str):
    """排序用：解析失败落到最小时间，保证稳定排序。"""
    return _parse_dt(s) or datetime.min


def week_bounds() -> tuple:
    """返回本周一 00:00 与当前时刻（本地朴素时间）。"""
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return monday, now


def fetch_week_docs() -> list:
    """返回本周（周一 00:00 至今）新录入的熔知文档 payload，按时间降序。"""
    monday, _ = week_bounds()
    docs = []
    for d in scroll_payloads():
        dt = _parse_dt(d.get("created_at") or "")
        if dt is None:
            continue
        if dt >= monday:
            docs.append(d)
    return docs


def search_docs(query: str, limit: int = 10) -> list:
    """在熔知文档 payload 中做大小写不敏感的子串匹配（标题/预览/主题/来源）。"""
    q = (query or "").strip().lower()
    if not q:
        return []
    hits = []
    for d in scroll_payloads():
        hay = " ".join([
            str(d.get("title") or ""),
            str(d.get("content_preview") or ""),
            " ".join(d.get("domain") or []),
            str(d.get("source") or ""),
        ]).lower()
        if q in hay:
            hits.append(d)
            if len(hits) >= limit:
                break
    return hits
