"""
core/qdrant_bridge.py — 巨作 ↔ 熔知 数据桥

【变更声明 · 2026-08-01 · AI 设计决策，非用户指令，待确认】
本桥由「纯只读」改为「读全量 + 单字段(stats.starred)受控写」：
  - 全模块唯一写入口：set_starred()；可写字段受白名单 WRITABLE_PAYLOAD_KEYS 约束，
    新增可写字段必须先改白名单；
  - 其余读取函数（fetch_week_docs / search_docs 等）行为保持不变，向后兼容；
  - 渲染用瞬态标记（_starred / _this_week，下划线前缀）仅供本次渲染使用，严禁回写 Qdrant。
该改动是 AI 为实现看板「收藏持久化」而作的设计决策，并非用户下达的指令，待用户确认；
若不认可，回滚方式 = 删除 set_starred() + 看板收藏按钮改为跳转熔知操作。

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

【数据 schema 注意 · 2026-07-31 修正】
熔知更新后，文档 payload 不再有顶层 created_at / content_preview：
  - 时间戳改为嵌套在 timeline 字典里：
      timeline.ingested  （录入知识库时间，优先用于「本周新录入」）
      timeline.published （原始内容发布时间）
      timeline.effective （生效时间）
  - 文档按 doc_id 切成多个 chunk 存入（chunk_index / total_chunks），
    因此周看板按 doc_id 去重，一篇文档只计一次。
  - 文本类字段现为 text / auto_summary / subject / keywords / domain，
    不再有 content_preview。

这是 MVP 路径；等熔知补齐官方读取 API 后，可平滑切换到 API 调用。
"""

import json
import os
import urllib.request
from datetime import datetime, timedelta

# 默认值与熔知当前配置保持一致；可在巨作 .env 覆盖
QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333").rstrip("/")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "athanor_v1")

# 可写 payload 字段白名单（围栏）：全模块只允许 set_starred() 发写请求，
# 且只允许写这里列出的字段。新增可写字段必须先改此行。
WRITABLE_PAYLOAD_KEYS = frozenset({"stats.starred"})


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


def _parse_dt(s: str):
    """把 ISO 时间字符串解析成朴素 datetime。

    先转到本地时区再丢弃时区信息，保证和 week_bounds() 产出的本地时间可比较
    （MVP 简化：不纠结 UTC 偏移，只求「本周」粒度正确）。
    """
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)
    return dt


def _doc_timestamp(d: dict):
    """从（新/旧两种）schema 取最佳可用时间戳，返回朴素本地 datetime 或 None。

    优先级：timeline.ingested > timeline.published > timeline.effective
            > 顶层 created_at / updated_at（兼容旧数据）。
    """
    tl = d.get("timeline")
    if isinstance(tl, dict):
        for key in ("ingested", "published", "effective"):
            v = tl.get(key)
            if v:
                dt = _parse_dt(v)
                if dt is not None:
                    return dt
    # 兼容旧 schema（顶层时间字段）
    for key in ("created_at", "updated_at", "created"):
        v = d.get(key)
        if v:
            dt = _parse_dt(v)
            if dt is not None:
                return dt
    return None


def scroll_payloads(limit: int = 200) -> list:
    """翻页拉取集合内全部文档 payload，按时间降序返回。

    返回 list[dict]，每个元素是熔知写入的文档 payload 字段
    （doc_id / title / source / source_project / timeline / content_type ...）。
    注意：payload 是按 doc_id 切分的 chunk，同 doc_id 会出现多次。
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
    out.sort(key=lambda d: _doc_timestamp(d) or datetime.min, reverse=True)
    return out


def week_bounds() -> tuple:
    """返回本周一 00:00 与当前时刻（本地朴素时间）。"""
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return monday, now


def fetch_week_docs() -> list:
    """返回本周（周一 00:00 至今）新录入的熔知文档，按 doc_id 去重、时间降序。

    以 timeline.ingested（录入时间）为主判据，落在「本周」内的文档才计入；
    同 doc_id 的多个 chunk 只保留首条，避免一篇文档被计多次。
    """
    monday, _ = week_bounds()
    seen = set()
    docs = []
    for d in scroll_payloads():
        dt = _doc_timestamp(d)
        if dt is None:
            continue
        if dt < monday:
            continue
        doc_id = d.get("doc_id")
        if doc_id in seen:
            continue
        seen.add(doc_id)
        docs.append(d)
    return docs


def search_docs(query: str, limit: int = 10) -> list:
    """在熔知文档 payload 中做大小写不敏感的子串匹配（标题/正文/摘要/主题/来源）。"""
    q = (query or "").strip().lower()
    if not q:
        return []
    seen = set()
    hits = []
    for d in scroll_payloads():
        doc_id = d.get("doc_id")
        if doc_id in seen:
            continue
        hay = " ".join([
            str(d.get("title") or ""),
            str(d.get("text") or ""),
            str(d.get("auto_summary") or ""),
            str(d.get("subject") or ""),
            " ".join(d.get("keywords") or []),
            str(d.get("source") or ""),
            str(d.get("source_project") or ""),
        ]).lower()
        if q in hay:
            seen.add(doc_id)
            hits.append(d)
            if len(hits) >= limit:
                break
    return hits


# ═══════════════════════════════════════════════════════════
# 收藏（stats.starred）—— 受控写 + 读取辅助
# ═══════════════════════════════════════════════════════════
def is_starred(d: dict) -> bool:
    """三层容错读取 stats.starred：stats 缺失 / stats 非 dict / starred 缺失 → False。

    业务代码一律走本函数，禁止手写 d["stats"]["starred"]（会 KeyError/TypeError）。
    """
    stats = d.get("stats")
    if not isinstance(stats, dict):
        return False
    return bool(stats.get("starred", False))


def count_doc_points(doc_id: str, *, timeout: int = 8) -> int:
    """数某 doc_id 在集合中的 chunk 点数（exact 精确计数）；异常返 0。

    Qdrant 对「匹配 0 点」的 set_payload 也返回 completed，必须先 count
    才能区分「写成功」与「doc 不存在」。
    """
    try:
        body = {
            "exact": True,
            "filter": {"must": [{"key": "doc_id", "match": {"value": doc_id}}]},
        }
        res = _post("points/count", body, timeout=timeout)
        return int((res.get("result") or {}).get("count") or 0)
    except Exception:
        return 0


def set_starred(doc_id: str, value: bool, *, timeout: int = 8) -> dict:
    """把某文档所有 chunk 的 stats.starred 置为 value。全模块唯一写入口。

    返回契约（永不抛异常）：
      {ok: bool, doc_id: str, starred: bool, updated: int, error: str | None}
    - ok=True 表示写入完成；updated 为该 doc 覆盖的 chunk 点数。
    - 任一异常都被捕获，转为 ok=False + error 信息。

    三要素缺一不可（见 docs/plan-dashboard-links-favorites.md §6 踩坑清单）：
      ① ?wait=true     —— 同步落盘，避免刷新读旧值「点了没反应」；
      ② key:"stats"    —— 嵌套合并，保留 access_count（漏了会整体替换 stats，不可逆）；
      ③ filter:{doc_id}—— 一次覆盖该 doc 全部 chunk（免前置 scroll 拿 point id 列表）。
    """
    base = {"ok": False, "doc_id": doc_id, "starred": bool(value), "updated": 0, "error": None}
    try:
        # ① 先 count 区分「写成功」与「doc 不存在」。
        n = count_doc_points(doc_id, timeout=timeout)
        if n <= 0:
            base["error"] = f"doc_id={doc_id!r} 在集合 {QDRANT_COLLECTION} 中不存在（0 个 chunk）"
            return base
        # ② 再 set_payload（带 wait=true / key="stats" / filter=doc_id）。
        body = {
            "payload": {"starred": bool(value)},
            "key": "stats",
            "filter": {"must": [{"key": "doc_id", "match": {"value": doc_id}}]},
        }
        res = _post("points/payload?wait=true", body, timeout=timeout)
        if (res.get("result") or {}).get("status") != "completed":
            base["error"] = f"set_payload 未完成：{res}"
            return base
        base.update({"ok": True, "updated": n})
        return base
    except Exception as e:  # noqa: BLE001 —— 契约要求永不抛异常
        base["error"] = f"{type(e).__name__}: {e}"
        return base


def fetch_dashboard_docs() -> dict:
    """单次全量 scroll，按 doc_id 去重，给每个 doc 打瞬态标记。

    返回 {week: [...], starred: [...], monday, now}：
      - week:    本周新录入（_this_week=True），时间降序；
      - starred: 已收藏（_starred=True），时间降序；
      - monday / now: 本周边界（本地朴素时间）。
    瞬态标记 _starred / _this_week 以下划线开头，仅供本次渲染使用，严禁回写 Qdrant。
    """
    monday, now = week_bounds()
    seen = set()
    docs = []
    for d in scroll_payloads():
        doc_id = d.get("doc_id")
        if not doc_id or doc_id in seen:
            continue
        seen.add(doc_id)
        d["_starred"] = is_starred(d)
        dt = _doc_timestamp(d)
        d["_this_week"] = dt is not None and dt >= monday
        docs.append(d)
    return {
        "week": [d for d in docs if d["_this_week"]],
        "starred": [d for d in docs if d["_starred"]],
        "monday": monday,
        "now": now,
    }


def fetch_starred_docs() -> list:
    """薄封装：只取已收藏文档列表（含瞬态标记 _starred/_this_week）。"""
    return fetch_dashboard_docs()["starred"]
