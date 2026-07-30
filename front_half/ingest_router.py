"""
巨作摄入入口 — 分类路由（模块 A1）

网页入口（pages/2_📥_摄入入口.py）与 AI 投递箱（front_half/drop_watcher.py）
共用本模块的唯一入口函数。

职责（严格按用户拍板）：
  - B站视频地址 → 展开 b23.tv 短链 → 投递到馏析队列(nigredo.core.queue.enqueue)
  - 本地文件（白名单 md/pdf/txt/png/jpg）→ 复制到熔知收件箱（筐②）
  - 闪念笔记（纯文本）→ 生成标准头 .md 写入熔知收件箱（筐②）
  - 非 B站 链接 → 拒收（巨作只收 B站 视频）

设计约束（来自用户硬约束）：
  - 队列不串 / 不误删 / 不残留（由 queue.py 三态+锁保证，这里只调用）
  - 不生成管理文件无限记录、不堆积垃圾（文件/笔记只落收件箱，投递箱 json 捡到即删）
"""
from __future__ import annotations

import json
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

logger = logging.getLogger("opus.ingest_router")

# ── 路径常量 ────────────────────────────────────────────────
# 筐②（炼真→熔知收件箱）= 熔知 WATCH_V2_INBOX_DIR = "library/inbox"
# 与 D:\citrinitas\config\settings.py:194 保持一致，不要各自写死漂移。
CITRINITAS_INBOX = r"D:\citrinitas\library\inbox"

# 文件白名单（巨作只收这些，避免把无关大文件丢进知识库）
ALLOWED_EXT = {".md", ".pdf", ".txt", ".png", ".jpg", ".jpeg"}

# 馏析项目根（用于调用其队列接口）
NIGREDO_PATH = r"D:\nigredo"


def _ensure_nigredo_importable() -> None:
    if NIGREDO_PATH not in sys.path:
        sys.path.insert(0, NIGREDO_PATH)


def is_bilibili_url(url: str) -> bool:
    """判断是不是 B站 地址（含 b23.tv 短链）。"""
    u = (url or "").strip().lower()
    return ("bilibili.com" in u) or ("b23.tv" in u)


def _expand_b23(url: str) -> str:
    """把 b23.tv 短链展开成完整 bilibili 地址（跟随重定向）。

    仅在处理 b23.tv 时才联网；展开失败显式报错，绝不静默吞掉。
    """
    import requests

    try:
        r = requests.get(url, allow_redirects=True, timeout=10)
        final = r.url
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"无法展开 b23.tv 短链（网络不可用？）: {e}")
    if not is_bilibili_url(final):
        raise RuntimeError(f"b23.tv 展开后不是 B站 地址: {final}")
    return final


def _enqueue_to_nigredo(url: str) -> int:
    _ensure_nigredo_importable()
    from core.queue import enqueue

    return enqueue(url)


# 仅保留的语义参数：分P（p）。默认页(p=1)视为无参数，剥掉以统一 doc_id，
# 避免同一视频因不同分享来源（buvid/share_source/unique_k/up_id/spmid...）算出不同 doc_id → 重复入库。
_BILI_KEEP_PARAMS = {"p"}


def _clean_bilibili_url(url: str) -> str:
    """剥掉 B站 分享链自带的跟踪参数，只保留语义相关的分P（p，且非默认页）。

    根因修复（用户拍板"剥掉"）：b23.tv 展开后的完整地址带一堆归因参数
    （buvid / from_spmid / share_source / unique_k / up_id / spmid / timestamp ...），
    同一视频不同分享来源参数不同 → doc_id 不同 → 重复入库。
    规范化成「BV 路径 + 仅分P」，与下游 doc_id 计算对齐，重复分享同一视频自动去重。
    """
    parts = urlsplit(url)
    kept = []
    for k, v in parse_qsl(parts.query, keep_blank_values=False):
        if k in _BILI_KEEP_PARAMS and not (k == "p" and v == "1"):
            kept.append((k, v))
    return urlunsplit(parts._replace(query=urlencode(kept)))


# ── 三类投递实现 ────────────────────────────────────────────
def route_bilibili(url: str) -> dict:
    """B站视频地址 → 展开 b23.tv → 投递馏析队列。"""
    url = (url or "").strip()
    if not url:
        return {"ok": False, "kind": "bilibili", "message": "地址为空"}
    if not is_bilibili_url(url):
        return {"ok": False, "kind": "bilibili", "message": "不是 B站 地址，已拒收"}
    try:
        real = _expand_b23(url) if "b23.tv" in url.lower() else url
        real = _clean_bilibili_url(real)
    except RuntimeError as e:
        return {"ok": False, "kind": "bilibili", "message": str(e)}
    try:
        n = _enqueue_to_nigredo(real)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "kind": "bilibili", "message": f"入队失败: {e}"}
    return {
        "ok": True,
        "kind": "bilibili",
        "message": f"已加入馏析队列（当前 {n} 个待处理）: {real}",
    }


def _safe_copy_to_inbox(src: Path) -> dict:
    ext = src.suffix.lower()
    if ext not in ALLOWED_EXT:
        return {
            "ok": False,
            "kind": "file",
            "message": f"不支持的文件类型 {ext}（仅允许 {sorted(ALLOWED_EXT)}）",
        }
    inbox = Path(CITRINITAS_INBOX)
    inbox.mkdir(parents=True, exist_ok=True)
    dest = inbox / src.name
    # 重名防覆盖：加时间戳后缀（避免误删/覆盖既有文件，满足"不误删"硬约束）
    if dest.exists():
        stem, suffix = src.stem, src.suffix
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        dest = inbox / f"{stem}_{ts}{suffix}"
    shutil.copy2(src, dest)
    return {"ok": True, "kind": "file", "message": f"已送入熔知收件箱: {dest.name}"}


def route_file(path: str) -> dict:
    """本地文件 → 白名单校验 → 复制到熔知收件箱（筐②）。"""
    if not path:
        return {"ok": False, "kind": "file", "message": "文件路径为空"}
    p = Path(path)
    if not p.exists():
        return {"ok": False, "kind": "file", "message": f"文件不存在: {path}"}
    if not p.is_file():
        return {"ok": False, "kind": "file", "message": f"不是文件: {path}"}
    return _safe_copy_to_inbox(p)


def route_note(text: str, title: str = "") -> dict:
    """闪念笔记（纯文本）→ 生成标准头 .md → 写入熔知收件箱。"""
    text = (text or "").strip()
    if not text:
        return {"ok": False, "kind": "note", "message": "笔记内容为空"}
    inbox = Path(CITRINITAS_INBOX)
    inbox.mkdir(parents=True, exist_ok=True)
    ts = datetime.now()
    iso = ts.replace(tzinfo=timezone.utc).isoformat()
    raw_slug = (title or text.split("\n")[0])[:20].strip() or "note"
    slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in raw_slug)
    fname = f"note_{ts.strftime('%Y%m%d-%H%M%S')}_{slug}.md"
    content = (
        "---\n"
        f"title: 闪念笔记 {slug}\n"
        "source: opus-magnum-note\n"
        f"created_at: {iso}\n"
        "type: note\n"
        "---\n\n"
        f"{text}\n"
    )
    dest = inbox / fname
    dest.write_text(content, encoding="utf-8")
    return {"ok": True, "kind": "note", "message": f"已写入熔知收件箱: {fname}"}


def route(payload: dict) -> dict:
    """统一入口（AI 投递箱用）。

    payload: {"type": "url"|"file"|"note", "value": ...}
    返回: {"ok": bool, "kind": str, "message": str}
    """
    if not isinstance(payload, dict):
        return {"ok": False, "kind": "unknown", "message": "投递格式错误（需 JSON 对象）"}
    ptype = payload.get("type")
    value = payload.get("value")
    if ptype == "url":
        u = str(value).strip()
        if not is_bilibili_url(u):
            return {"ok": False, "kind": "url", "message": "非 B站 链接，巨作只收 B站 视频（已拒收）"}
        return route_bilibili(u)
    if ptype == "file":
        return route_file(str(value))
    if ptype == "note":
        return route_note(str(value))
    return {"ok": False, "kind": "unknown", "message": f"未知投递类型: {ptype}"}


if __name__ == "__main__":
    # 纯分类冒烟：不联网、不落文件、不入队（避免污染真实收件箱/队列）
    logging.basicConfig(level=logging.INFO)
    assert is_bilibili_url("https://www.bilibili.com/video/BV1xx411c7mD")
    assert is_bilibili_url("https://b23.tv/abcd")
    assert not is_bilibili_url("https://www.youtube.com/watch?v=abc")
    # 非 B站 链接应在 route 层被拒收（不触发入队/网络）
    r = route({"type": "url", "value": "https://www.youtube.com/watch?v=abc"})
    assert r["ok"] is False and "拒收" in r["message"], r
    print("ingest_router 分类冒烟通过：B站识别 / 非B站拒收 均正确")
