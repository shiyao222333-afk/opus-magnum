"""
OpusMagnum · 巨作 / GreatWork — 一人公司总指挥部

门户化布局（2026-08-03 重构）：顶部导航条（品牌 + 图标页签 + 系统状态 + 外链 + 🏠总指挥部跳 Dashy）。
  - /         → 周看板（本周新录入；2026-08-04 起入口让位行动清单，页面保留无入口）
  - /ingest   → 摄入入口（投递 + 三器启停 + 队列 + 日志）
  - /control  → 五器控制台（一键开关五器服务 + 动态状态灯）
  - /hq       → 总指挥部（健康 / GitHub / 任务 / 路线）
  - 🏠 总指挥部 → Dashy 4000（唯一大门，承接原 /wall 显示墙功能）
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from nicegui import app, run, ui

from config.settings import settings
from core.qdrant_bridge import (
    fetch_dashboard_docs,
    is_starred,
    qdrant_reachable,
    set_starred,
    week_bounds,
)
from core.health_check import check_all
from core.dashboard import get_all_repo_summaries, get_all_tasks
from front_half.ingest_router import route_bilibili, route_file, route_note
from front_half.supervisor.launcher import (
    LOGS_DIR, SERVICES, is_running,
    start_all as launcher_start_all, start_service,
    stop_all as launcher_stop_all, stop_service,
)

QUEUE_FILE = Path(r"D:\nigredo\data\queue.json")
UPLOAD_TMP = PROJECT_ROOT / "drop" / "_upload_tmp"
UPLOAD_TMP.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════
# 共享辅助
# ═══════════════════════════════════════════════════════════
def _notify_res(res: dict) -> None:
    if res.get("ok"):
        ui.notify(res.get("message", "完成"), type="positive")
    else:
        ui.notify(res.get("message", "失败"), type="negative")


# ═══════════════════════════════════════════════════════════
# 顶部导航条（门户化后取代左抽屉，对齐熔知风格）
# 品牌 + 图标页签（摄入/总指挥，周看板已让位行动清单）+ 系统状态徽章 + 外链 + 🏠总指挥部(Dashy 大门)
# ═══════════════════════════════════════════════════════════
def _nav_class_top(page_key) -> str:
    """当前页高亮（蓝紫），其他页悬停变深。"""
    active = getattr(ui, "_active_opus_page", "")
    if active == page_key:
        return "px-3 py-1.5 rounded bg-blue-700 no-underline text-white font-bold"
    return "px-3 py-1.5 rounded hover:bg-blue-700 transition no-underline text-white/85"


def build_top_bar(active_page: str = "") -> None:
    """顶部导航条：品牌 + 图标页签 + 系统状态 + 外链 + 🏠 总指挥部（跳 Dashy 大门）。"""
    # 存当前页面标识，供 _nav_class_top 使用
    ui._active_opus_page = active_page

    with ui.header().classes("bg-gray-900 text-white") as header:
        with ui.row().classes("w-full items-center px-4 py-2 gap-3"):
            # 品牌
            ui.markdown("**⚛️ 巨作**").classes("text-lg mr-1")

            # 图标页签（业务页面入口；周看板 2026-08-04 起让位行动清单，页面保留无入口；
            # 显示墙由 🏠 总指挥部 = Dashy 承担）
            with ui.row().classes("items-center gap-1"):
                ui.link("📥 摄入", "/ingest").classes(_nav_class_top("ingest"))
                ui.link("🎛️ 总指挥", "/hq").classes(_nav_class_top("hq"))

            # 弹性空隙，把右侧信息推到最右
            ui.space()

            # 系统状态（每页可见，保持抽屉时代的"随时看状态"）
            _qdrant_ok = qdrant_reachable()
            ui.badge("Qdrant " + ("在线" if _qdrant_ok else "离线"),
                     color="green" if _qdrant_ok else "red")
            _web_keys = [s["key"] for s in SERVICES if s.get("web_visible")]
            _running = sum(1 for k in _web_keys if is_running(k))
            _total = len(_web_keys)
            ui.label(f"服务 {_running}/{_total}").classes("text-xs text-gray-300")

            # 外链（保留抽屉时代的外链）
            ui.link("🔗 熔知", settings.citrinitas.endpoint("/")).classes("text-xs text-blue-300")
            ui.link("🔗 GitHub", "https://github.com/shiyao222333-afk/OpusMagnum").classes("text-xs text-blue-300")

            # 🏠 总指挥部 = Dashy 大门（新标签打开，替代原"显示墙"巨作内嵌）
            ui.link("🏠 总指挥部", "http://localhost:4000", new_tab=True).classes(
                "px-3 py-1 rounded bg-amber-600 text-white text-sm font-bold no-underline"
            )

        return header


# ═══════════════════════════════════════════════════════════
# 周看板辅助：熔知可达性探测 + 收藏交互 + 单行渲染 + 可刷新主体
# ═══════════════════════════════════════════════════════════

# 内容类型人话显示名（看板分组用）
# 复制自熔知 classifications.py 的 CONTENT_TYPE_OPTIONS（仅取显示名），
# 熔知改词表需同步；禁止 import 熔知模块（五器独立原则）。
CONTENT_TYPE_LABELS = {
    "knowledge":     "📖 知识条目",
    "document":      "📄 原始文档",
    "video_script":  "🎬 视频脚本",
    "social_post":   "📱 社媒文案",
    "article":       "📰 文章/博客",
    "book":          "📚 书籍",
    "paper":         "📑 学术论文",
    "standard":      "📜 标准/规范",
    "webpage":       "🌐 网页内容",
    "personal_note": "📝 个人笔记",
    "project_note":  "📋 项目笔记",
    "idea":          "💡 想法/灵感",
    "template":      "📐 模板",
    "legal_doc":     "⚖️ 法律文件",
    "other":         "📦 其它",
}


def _citrinitas_reachable() -> bool:
    """探测熔知 8080 是否可达（决定标题外链 vs 本地弹窗兜底）。

    零新依赖：仅标准库 urllib，GET 熔知根路径即可判定进程在不在。
    """
    try:
        url = settings.citrinitas.endpoint("/")
        with urllib.request.urlopen(url, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def _preview_line(label: str, value) -> None:
    """本地预览弹窗里的一行；值为空则整行省略。"""
    if value is None or value == "" or value == []:
        return
    ui.label(f"{label}：{value}").classes("text-sm")


def _doc_row(d: dict, online: bool) -> None:
    """渲染一行文档：★收藏按钮 + 标题（外链熔知 / 离线降级弹窗）+ 👁本地预览兜底。

    - online=True  → 标题外链熔知 /doc/{doc_id}（新标签页）；
    - online=False → 熔知不可达，标题降级为点击打开本地预览弹窗。
    - 👁 本地预览按钮始终存在作为兜底，展示 title / auto_summary / subject /
      keywords / source / timeline / text（text 截断）。
    - 已收藏条目 ★ 黄色高亮（按钮 + 标题均变黄）。
    """
    starred = bool(d.get("_starred", is_starred(d)))
    title = (d.get("title") or "(无标题)")[:40]
    doc_id = d["doc_id"]
    detail_url = settings.citrinitas.endpoint(f"/doc/{doc_id}")

    # 本地预览弹窗（每行一个，互不干扰）
    preview_dialog = ui.dialog()
    with preview_dialog, ui.card().classes("w-[560px] max-w-[90vw] p-4"):
        ui.label(title).classes("text-lg font-bold text-blue-200")
        ui.separator()
        _preview_line("主题", d.get("subject"))
        _preview_line("关键词", "、".join(d.get("keywords") or []))
        _preview_line("来源", d.get("source"))
        _preview_line("来源项目", d.get("source_project"))
        timeline = d.get("timeline") or {}
        _preview_line("录入时间", timeline.get("ingested") if isinstance(timeline, dict) else None)
        _preview_line("摘要", d.get("auto_summary"))
        text = (d.get("text") or "").strip()
        if len(text) > 1500:
            text = text[:1500] + " ……（正文截断，完整内容请到熔知查看）"
        _preview_line("正文", text)
        with ui.row().classes("w-full justify-end mt-2"):
            ui.button("关闭", on_click=preview_dialog.close).props("flat")

    with ui.row().classes("w-full items-center gap-2"):
        star_btn = ui.button("★" if starred else "☆").props("flat round dense size=sm")
        star_btn.classes("text-yellow-300" if starred else "text-gray-400")
        star_btn.on_click(lambda d=d, btn=star_btn: _on_toggle_star(d, btn))

        title_class = "text-sm no-underline " + ("text-yellow-200" if starred else "text-blue-300")
        if online:
            ui.link(title, detail_url, new_tab=True).classes(title_class)
        else:
            # 熔知离线降级：ui.link 无 on_click 参数，改用元素事件绑定（on() 支持同步 handler）
            ui.link(title).on("click", preview_dialog.open).classes(title_class)

        ui.button("👁", on_click=preview_dialog.open).props("flat round dense size=sm").classes("text-blue-300")
        ui.tooltip("本地预览（熔知离线兜底）")


async def _on_toggle_star(d: dict, btn) -> None:
    """async 收藏切换：先 disable 防连点 → io_bound 写 Qdrant → 成功刷新 / 失败恢复。

    ui.notify 的 positive/negative 按 set_starred 返回的 ok 区分。
    """
    new_val = not d.get("_starred", False)
    btn.disable()
    res = await run.io_bound(set_starred, d["doc_id"], new_val)
    if res.get("ok"):
        ui.notify(
            ("⭐ 已收藏 " if new_val else "已取消收藏 ") + (d.get("title") or "")[:20],
            type="positive",
        )
        dashboard_body.refresh()
    else:
        ui.notify(f"收藏操作失败：{res.get('error')}", type="negative")
        btn.enable()


@ui.refreshable
def dashboard_body() -> None:
    """看板主体（可局部刷新，不用 ui.update() 或整页跳转）。

    布局：顶部总览条（本周篇数 / 来源数 / 收藏数）→ ⭐ 收藏区置顶（前 20 + 共 N 篇计数）
    → 📥 本周区在下按 content_type 人话分类，两列等宽卡片。
    两区默认双显、各自 doc_id 去重；空态保留「📭 本周还没有新录入。」。
    """
    data = fetch_dashboard_docs()
    week_docs = data["week"]
    starred_docs = data["starred"]
    online = _citrinitas_reachable()

    # 空态：两区都空
    if not week_docs and not starred_docs:
        with ui.card().classes("w-full"):
            ui.label("📭 本周还没有新录入。").classes("text-gray-400")
        return

    # ── T1 顶部总览条：3 个等宽数字卡（本周篇数 / 来源数 / 收藏数）──
    n_week = len(week_docs)
    n_sources = len({
        d.get("source_project") or d.get("source") or "未知来源"
        for d in week_docs
    })
    n_starred = len(starred_docs)
    with ui.grid(columns=3).classes("gap-4 w-full"):
        with ui.card().classes("w-full"):
            with ui.column().classes("items-center"):
                ui.label(f"{n_week}").classes("text-2xl font-bold text-blue-300")
                ui.label("本周篇数").classes("text-xs text-gray-400")
        with ui.card().classes("w-full"):
            with ui.column().classes("items-center"):
                ui.label(f"{n_sources}").classes("text-2xl font-bold text-blue-300")
                ui.label("来源数").classes("text-xs text-gray-400")
        with ui.card().classes("w-full"):
            with ui.column().classes("items-center"):
                ui.label(f"{n_starred}").classes("text-2xl font-bold text-yellow-300")
                ui.label("⭐ 收藏").classes("text-xs text-gray-400")

    # ── T4 ⭐ 收藏区（置顶、全宽列表，保持现状：每行 _doc_row = ★ + 标题 + 👁）──
    if starred_docs:
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full items-center gap-3"):
                ui.label("⭐ 收藏区").classes("font-bold text-lg text-yellow-300")
                ui.badge(f"共 {len(starred_docs)} 篇", color="yellow-8", outline=True)
            ui.separator()
            for d in starred_docs[:20]:
                _doc_row(d, online)

    # ── T2/T3 📥 本周区：按 content_type 人话分类，两列等宽卡片 ──
    with ui.card().classes("w-full"):
        with ui.row().classes("w-full items-center gap-3"):
            ui.label("📥 本周新录入").classes("font-bold text-lg text-blue-300")
            ui.badge(f"{len(week_docs)} 篇", color="blue-8", outline=True)
        ui.separator()
        if not week_docs:
            ui.label("（本周暂无新录入）").classes("text-sm text-gray-400")
        else:
            # 分组键：content_type（缺失/未知 → "其他"），标题用人话 emoji 显示名
            groups: dict = {}
            for d in week_docs:
                key = d.get("content_type")
                label = CONTENT_TYPE_LABELS.get(key, "其他")
                groups.setdefault((key, label), []).append(d)
            for (key, label), items in groups.items():
                with ui.row().classes("w-full items-center gap-3 mt-2"):
                    ui.label(label).classes("font-bold text-sm text-blue-200")
                    ui.label(f"{len(items)} 篇").classes("text-xs text-gray-400")
                # 两列等宽卡片，每张卡片极简：★收藏 + 标题 + 👁本地预览（一行）
                with ui.grid(columns=2).classes("gap-4 w-full"):
                    for d in items[:8]:
                        with ui.card().classes("w-full"):
                            _doc_row(d, online)


# ═══════════════════════════════════════════════════════════
# 页面: 周看板 (/)
# ═══════════════════════════════════════════════════════════
@ui.page("/")
def page_dashboard():
    build_top_bar("")
    with ui.column().classes("w-full p-6"):
        ui.markdown("## 📊 周看板")
        monday, now = week_bounds()
        ui.label(
            f"周一 {monday.strftime('%Y-%m-%d')} ～ 今天 {now.strftime('%Y-%m-%d')} ｜ 数据来自 熔知"
        ).classes("text-sm text-gray-400 mb-4")

        if not qdrant_reachable():
            ui.label("⚠️ 连不上熔知数据库（Qdrant）。").classes("text-orange-400")
            return

        dashboard_body()


# ═══════════════════════════════════════════════════════════
# 页面: 摄入入口 (/ingest)
# ═══════════════════════════════════════════════════════════
@ui.page("/ingest")
def page_ingest():
    build_top_bar("ingest")
    with ui.column().classes("w-full p-6"):
        ui.markdown("## 📥 摄入入口")

        # ① 投递
        ui.markdown("### 投递")
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full items-end"):
                bili_input = ui.input(
                    "B站链接（支持 b23.tv 短链）",
                    placeholder="https://www.bilibili.com/video/BV...",
                ).classes("flex-grow")
                ui.button("加入馏析队列",
                          on_click=lambda: _notify_res(route_bilibili(bili_input.value or ""))).props("color=blue")
            ui.separator()
            ui.upload(on_upload=lambda e: [
                _notify_res(route_file(str(_write_tmp(f))))
                for f in e
            ], multiple=True).classes("w-full")
            ui.label("支持 epub / html / htm / pdf / txt / md / json / csv / srt / docx / pptx / 图片(jpg/jpeg/png/tiff/bmp/webp)，≤50MB → 送入熔知收件箱").classes("text-xs text-gray-400")
            ui.separator()
            note_area = ui.textarea("闪念笔记（生成标准 .md 送入熔知收件箱）").classes("w-full")
            ui.button("保存笔记",
                      on_click=lambda: _notify_res(route_note(note_area.value or ""))).props("color=blue outline")

        # ② 三器启停
        ui.markdown("### 三器启停")
        ui.label("打开本页不会自动启动任何服务；关闭网页也不会杀掉它们。").classes("text-xs text-gray-400")
        with ui.card().classes("w-full"):
            with ui.row().classes("gap-2"):
                ui.button("一键启动摄入管线", on_click=launcher_start_all).props("color=positive")
                ui.button("一键停止摄入管线", on_click=launcher_stop_all).props("color=negative")
            ui.separator()
            # 只展示 web_visible 的服务
            for s in [s for s in SERVICES if s.get("web_visible")]:
                name = s["key"]
                spec = s
                running = is_running(name)
                badge = "🟢" if running else "🔴"
                with ui.card().classes("w-full"):
                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label(f"{badge} {spec['label']}").classes("font-bold text-sm")
                        with ui.row().classes("gap-1"):
                            ui.button("启动", on_click=lambda n=name: start_service(n)).props("outline size=sm color=positive")
                            ui.button("停止", on_click=lambda n=name: stop_service(n)).props("outline size=sm color=negative")

        # ③ 馏析队列概览
        ui.markdown("### 馏析队列概览")
        total = pending = processing = 0
        if QUEUE_FILE.exists():
            try:
                items = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
                total = len(items)
                pending = sum(1 for i in items if i.get("status") == "pending")
                processing = sum(1 for i in items if i.get("status") == "processing")
            except Exception:
                pass
        with ui.card().classes("w-full"):
            with ui.row().classes("gap-8"):
                with ui.column().classes("items-center"):
                    ui.label(f"{total}").classes("text-2xl font-bold text-blue-300")
                    ui.label("总数").classes("text-xs text-gray-400")
                with ui.column().classes("items-center"):
                    ui.label(f"{pending}").classes("text-2xl font-bold text-yellow-300")
                    ui.label("待处理").classes("text-xs text-gray-400")
                with ui.column().classes("items-center"):
                    ui.label(f"{processing}").classes("text-2xl font-bold text-green-300")
                    ui.label("处理中").classes("text-xs text-gray-400")

        # ④ 日志
        ui.markdown("### 服务日志")
        for s in [s for s in SERVICES if s.get("web_visible")]:
            name = s["key"]
            spec = s
            with ui.expansion(f"📜 {spec['label']}").classes("w-full"):
                p = LOGS_DIR / f"{name}.log"
                if p.exists():
                    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
                    txt = "\n".join(lines[-200:])
                else:
                    txt = "(服务未启动或未产生输出)"
                ui.code(txt).classes("w-full text-xs")


def _write_tmp(f):
    tmp = UPLOAD_TMP / f.name
    tmp.write_bytes(f.content)
    return str(tmp)


# ═══════════════════════════════════════════════════════════
# 五器定义（控制台用）：key → (显示名, 图标, 网页URL or None)
# ═══════════════════════════════════════════════════════════
FIVE_VESSELS = [
    ("opus",       "巨作", "👑", "http://localhost:8501"),
    ("citrinitas", "熔知", "📖", "http://localhost:8080"),
    ("rubedo",     "凝华", "✨", "http://localhost:8081"),
    ("nigredo",    "馏析", "⚫", None),
    ("albedo",     "炼真", "🤍", None),
]


# ═══════════════════════════════════════════════════════════
# 页面: 五器控制台 (/control) — Dashy 门户的服务开关面板
# 复用 supervisor 启停接口；动态状态灯：🟢运行 / ⚪停止 / 🟡切换中
# ═══════════════════════════════════════════════════════════
@ui.page("/control")
def page_control():
    build_top_bar("control")
    with ui.column().classes("w-full p-6"):
        ui.markdown("## ⚙️ 五器控制台")
        ui.label("一键开关五器服务；状态灯实时刷新：🟢 运行 / ⚪ 停止 / 🟡 切换中。").classes("text-sm text-gray-400 mb-2")

        badges: dict = {}
        on_btns: dict = {}
        off_btns: dict = {}

        with ui.column().classes("w-full gap-2"):
            for key, name, icon, url in FIVE_VESSELS:
                with ui.card().classes("w-full"):
                    with ui.row().classes("w-full items-center justify-between"):
                        badge = ui.label("⏳").classes("text-xl w-8 text-center")
                        with ui.column().classes("gap-0"):
                            ui.label(f"{icon} {name}").classes("font-bold text-sm")
                            ui.label("有网页" if url else "仅服务（无网页）").classes("text-xs text-gray-500")
                        with ui.row().classes("gap-2 items-center"):
                            on_btn = ui.button("启动").props("outline size=sm color=positive")
                            off_btn = ui.button("停止").props("outline size=sm color=negative")
                            if url:
                                ui.link("打开网页", url).classes("text-blue-300 text-sm")
                        badges[key] = badge
                        on_btns[key] = on_btn
                        off_btns[key] = off_btn

        def refresh():
            for key, _n, _i, _u in FIVE_VESSELS:
                running = is_running(key)
                badges[key].text = "🟢" if running else "⚪"
                on_btns[key].props(f"disable={running}")
                off_btns[key].props(f"disable={not running}")

        def toggle(key: str, action: str):
            # 置切换中 + 禁按钮防连点
            badges[key].text = "🟡"
            on_btns[key].props("disable=True")
            off_btns[key].props("disable=True")
            try:
                if action == "start":
                    start_service(key)
                else:
                    stop_service(key)
            except Exception:
                badges[key].text = "⚠️"
            # 服务启停需要时间，稍后刷新状态
            ui.timer(2.5, refresh, once=True)

        for key, _n, _i, _u in FIVE_VESSELS:
            on_btns[key].on("click", lambda k=key: toggle(k, "start"))
            off_btns[key].on("click", lambda k=key: toggle(k, "stop"))

        refresh()              # 首屏状态
        ui.timer(5.0, refresh)  # 周期轮询（同步外部状态变化）


# ═══════════════════════════════════════════════════════════
# 页面: 总指挥部 (/hq)
# ═══════════════════════════════════════════════════════════
@ui.page("/hq")
def page_hq():
    build_top_bar("hq")
    with ui.column().classes("w-full p-6"):
        ui.markdown("## 🎛️ 总指挥部")

        # ① 服务健康
        ui.markdown("### 服务健康状态")
        with ui.card().classes("w-full"):
            for h in check_all():
                if h["online"]:
                    extra = f"{h.get('latency_ms')}ms" if h.get("latency_ms") else "在线"
                    ui.label(f"✅ {h['project']} — {extra}").classes("text-green-400")
                else:
                    ui.label(f"❌ {h['project']} — {h.get('status', 'unknown')}").classes("text-red-400")

        # ② GitHub 仓库
        ui.markdown("### GitHub 仓库状态")
        try:
            repo_sum = get_all_repo_summaries()
        except Exception as e:
            repo_sum = {}
            ui.label(f"⚠️ GitHub 读取失败：{e}").classes("text-orange-400")
        REPO_ALIAS = {
            "Citrinitas": "🏭 熔知", "Nigredo": "⚗️ 馏析",
            "Albedo": "🔬 炼真", "Rubedo": "✨ 凝华", "OpusMagnum": "⚛️ 巨作",
        }
        with ui.card().classes("w-full"):
            for key, alias in REPO_ALIAS.items():
                data = repo_sum.get(key, {})
                if "error" in data:
                    ui.label(f"{alias} — GitHub Token 未配置").classes("text-orange-400 text-sm")
                else:
                    ui.label(f"{alias} — {data.get('open_issues', 0)} issues · ⭐ {data.get('stars', 0)}").classes("text-sm")

        # ③ 任务看板
        ui.markdown("### 任务看板")
        try:
            tasks = get_all_tasks(state="open")
        except Exception as e:
            tasks = []
            ui.label(f"⚠️ 任务读取失败：{e}").classes("text-orange-400")
        with ui.card().classes("w-full"):
            if not tasks:
                ui.label("暂无任务数据。").classes("text-gray-400")
            else:
                done = sum(1 for t in tasks if t.get("status") == "done")
                ui.label(f"总任务 {len(tasks)} · 进行中 {len(tasks) - done} · 已完成 {done}").classes("font-bold")
                ui.separator()
                for t in tasks[:30]:
                    ui.label(f"[{t.get('project_label', '')}] {t.get('title', '')}").classes("text-sm")

        # ④ 开发路线
        ui.markdown("### 开发路线")
        with ui.card().classes("w-full"):
            ui.markdown(
                "| 阶段 | 项目 | 状态 |\n"
                "|------|------|:--:|\n"
                "| Phase 1 地基 | 🏭 熔知 | ✅ MVP |\n"
                "| Phase 2 摄取 | ⚗️ 馏析 | ✅ 可用 |\n"
                "| Phase 3 验证 | 🔬 炼真 | ✅ 可用 |\n"
                "| Phase 4 输出 | ✨ 凝华 | 进行中 |"
            )


# ═══════════════════════════════════════════════════════════
# 路由兜底 & 启动
# ═══════════════════════════════════════════════════════════
# 注：原 /wall（显示墙页，iframe 内嵌 Dashy）已按门户化方案删除——
#     🏠 总指挥部 = Dashy 4000 直接承担显示墙功能（顶部条橙色按钮跳转），
#     避免"巨作内嵌 Dashy"的循环嵌套。BUGLOG-显示墙iframe空白-0803 已归档。
@ui.page("/health")
def page_health():
    """总管探活端点"""
    return {"status": "ok", "project": "opus-magnum"}


if __name__ in {"__main__", "__mp_main__"}:
    # /health 注册为 API 端点（纯 JSON，不走页面渲染）
    @app.get("/api/health")
    def _health():
        return {"status": "ok", "project": "opus-magnum"}

    _show_browser = os.environ.get("OM_AUTO_OPEN_BROWSER", "1") != "0"
    ui.run(
        port=settings.opus_port,
        title="OpusMagnum · 巨作",
        reload=False,
        show=_show_browser,
        dark=True,
    )
