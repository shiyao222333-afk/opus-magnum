"""
巨作摄入入口 — 分类路由（模块 A1）

网页入口（pages/2_📥_摄入入口.py）与 AI 投递箱（front_half/drop_watcher.py）
共用本模块的唯一入口函数。

职责（严格按用户拍板）：
  - B站视频地址 → 展开 b23.tv 短链 → 投递到馏析队列(nigredo.core.queue.enqueue)
  - 本地文件（白名单对齐熔知 registry：epub/html/htm/pdf/txt/md/json/csv/srt/docx/pptx/
    jpg/jpeg/png/tiff/bmp/webp，上限 50MB）→ 复制到熔知收件箱（筐②），由熔知自行校验/提取
  - 闪念笔记（纯文本）→ 生成标准头 .md 写入熔知收件箱（筐②）
  - 非 B站 链接 → 拒收（巨作只收 B站 视频）
语义铁律（2026-08-02 用户拍板）：巨作的入口作用是「分类」——只有识别到 B站 网址才走
馏析→炼真→熔知管线；其他一切输入（各种格式文件/笔记）都直接给熔知收件箱（熔知 watcher
自己处理），不得走馏析管线。

设计约束（来自用户硬约束）：
  - 队列不串 / 不误删 / 不残留（由 queue.py 三态+锁保证，这里只调用）
  - 不生成管理文件无限记录、不堆积垃圾（文件/笔记只落收件箱，投递箱 json 捡到即删）
"""
from __future__ import annotations

import json
import logging
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

logger = logging.getLogger("opus.ingest_router")

# ── 复用 launcher.py 现成启停引擎（禁止自研检测/启动）────────────────
# 本模块可能被 drop_watcher 独立进程 import（此时 sys.path 只有 front_half/，
# 没有 D:\opus-magnum），包路径导入 front_half.supervisor.launcher 会失败；
# 故用绝对路径 importlib 加载（与 launcher.py 自身加载 services.py 的方式一致），
# 加载出的模块取别名 opus_ingest_launcher，不占用 launcher 这个名字。
import importlib.util as _ilu

_OPUS_ROOT = Path(__file__).resolve().parent.parent  # D:\opus-magnum
_LAUNCHER_FILE = _OPUS_ROOT / "front_half" / "supervisor" / "launcher.py"
_LAUNCHER_SPEC = _ilu.spec_from_file_location("opus_ingest_launcher", str(_LAUNCHER_FILE))
_LAUNCHER_MOD = _ilu.module_from_spec(_LAUNCHER_SPEC)
_LAUNCHER_SPEC.loader.exec_module(_LAUNCHER_MOD)

# ── 路径常量 ────────────────────────────────────────────────
# 筐②（炼真→熔知收件箱）= 熔知 WATCH_V2_INBOX_DIR = "library/inbox"
# 与 D:\citrinitas\config\settings.py:194 保持一致，不要各自写死漂移。
CITRINITAS_INBOX = r"D:\citrinitas\library\inbox"

# ⚠️ AI 模型禁止直接向熔知收件箱（D:\citrinitas\library\inbox）写入文件——
# 该目录摄入即入库即删源，警告文件也会被吃掉。所有投递必须走本文件的
# route()/route_* 或巨作网页「摄入入口」页。

# 文件白名单（对齐熔知 utils/file_handler/registry.py 的 FILE_TYPE_REGISTRY，17 个扩展名 / 15 类格式）：
#   层级1 自带元数据 : epub / html / htm
#   层级2 纯文本     : pdf / txt / md / json / csv / srt / docx / pptx
#   层级3 图片(OCR)  : jpg / jpeg / png / tiff / bmp / webp
# 巨作只做「薄放行」：白名单内的文件复制进熔知收件箱，由熔知 watcher 自行校验/提取；
# 不在白名单的格式拒收，避免把无关大文件丢进知识库。
ALLOWED_EXT = {
    ".epub", ".html", ".htm", ".pdf", ".txt", ".md",
    ".json", ".csv", ".srt", ".docx", ".pptx",
    ".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".webp",
}

# 文件大小上限（对齐熔知 registry.SIZE_LIMIT_MB = 50）：超过拒收，防止超大文件涌入收件箱
MAX_FILE_MB = 50
MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024

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


# ── 摄入前置：自动拉起缺失服务（2026-08-02 用户拍板）────────────────
# 投递摄入（B站/文件/笔记）时不检查馏析/炼真/熔知是否在跑，服务没起时内容会
# 卡在队列/收件箱没人处理。故每次投递在公共前置处先确保管线服务在位。
# 只检测/启动这四个 key；qdrant=数据底座、citrinitas=熔知、nigredo=馏析、albedo=炼真。
# 依赖顺序：qdrant → citrinitas（depends_on qdrant）→ nigredo → albedo（depends_on nigredo）。
# 启动顺序按依赖排列，靠 launcher.start_service 内部实现幂等（已跑返回 'already'）。
_INGEST_REQUIRED_SERVICES = ("qdrant", "citrinitas", "nigredo", "albedo")


def _ensure_ingest_services() -> dict:
    """摄入前置：检查摄入管线服务是否在跑，缺失的自动拉起。

    一切检测与启动都复用 launcher.py 现成的 is_running / start_service，
    禁止自研 HTTP 探测 / 进程名匹配（上次教训：重复造轮子且误杀自己）。

    返回结构化结果：
      {"started": [...], "already_running": [...], "failed": [...]}
    启动失败的服务如实记录（含原因，不吞异常），由调用方决定是否提示。
    """
    result: dict = {"started": [], "already_running": [], "failed": []}
    for key in _INGEST_REQUIRED_SERVICES:
        try:
            if _LAUNCHER_MOD.is_running(key):
                result["already_running"].append(key)
                continue
            status = _LAUNCHER_MOD.start_service(key)
            if status == "started":
                result["started"].append(key)
            elif status == "already":
                # 检查与启动之间存在竞态：启动函数发现已在跑，如实记为已运行
                result["already_running"].append(key)
            else:
                result["failed"].append({"key": key, "reason": status})
        except Exception as e:  # noqa: BLE001
            result["failed"].append({"key": key, "reason": str(e)})
    if result["started"] or result["failed"]:
        logger.info("摄入前置服务检查: started=%s already=%s failed=%s",
                    result["started"], result["already_running"], result["failed"])
    return result


# ── 三类投递实现 ────────────────────────────────────────────
def route_bilibili(url: str) -> dict:
    """B站视频地址 → 展开 b23.tv → 投递馏析队列。"""
    _ensure_ingest_services()
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
    try:
        size = src.stat().st_size
    except OSError:
        size = 0
    if size > MAX_FILE_BYTES:
        return {
            "ok": False,
            "kind": "file",
            "message": f"文件超过 {MAX_FILE_MB}MB 上限（{size / 1024 / 1024:.1f}MB），已拒收",
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
    _ensure_ingest_services()
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
    _ensure_ingest_services()
    # ── 调用栈日志（排查重复入库用） ──
    stack = "".join(traceback.format_stack()[:-1])
    logger.info("route_note 被调用 | title=%s | text[:50]=%s\n调用栈:\n%s",
                title, (text or "")[:50], stack)

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
        "author: 我\n"
        f"created_at: {iso}\n"
        "type: note\n"
        "---\n\n"
        f"{text}\n"
    )
    dest = inbox / fname
    dest.write_text(content, encoding="utf-8")
    logger.info("route_note 已落盘: %s", fname)
    return {"ok": True, "kind": "note", "message": f"已写入熔知收件箱: {fname}"}
    iso = ts.replace(tzinfo=timezone.utc).isoformat()
    fname = f"note_{ts.strftime('%Y%m%d-%H%M%S')}_{slug}.md"
    content = (
        "---\n"
        f"title: 闪念笔记 {slug}\n"
        "source: opus-magnum-note\n"
        "author: 我\n"
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
