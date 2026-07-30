"""
OpusMagnum · 巨作 / GreatWork — 一人公司总指挥部（NiceGUI 重写）

单页应用，三个标签页：
  ① 周看板：直读熔知共享 Qdrant，展示本周新录入。
  ② 摄入入口：投递（B站/文件/笔记）+ 三器启停 + 队列概览 + 日志。
  ③ 总指挥部：服务健康 + GitHub 仓库 + 任务看板 + API 规范 + 路线。

设计说明（AI 设计决策，非用户指令，待确认）：
  - 原 Streamlit 网页（app.py / pages/ / utils/ui_utils.py）已删除；
    原独立 Supervisor(:8503) 与摄入入口功能重复，已删除，摄入功能并入本页。
  - 已删除打「已下线的 8502/8503 网页 API」的手动联动按钮
    （对应 core/project_hub.py 的 alembic_*/crucible_* 死函数已清）。
  - 后端数据层（qdrant_bridge / health_check / dashboard / launcher / ingest_router）
    框架无关，直接复用，未做增殖。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from nicegui import ui

from config.settings import settings
from core.qdrant_bridge import fetch_week_docs, qdrant_reachable, week_bounds
from core.health_check import check_all
from core.dashboard import get_all_repo_summaries, get_all_tasks
from front_half.ingest_router import route_bilibili, route_file, route_note
from front_half.supervisor.launcher import (
    LOGS_DIR,
    SERVICES,
    is_running,
    start_all as launcher_start_all,
    start_service,
    stop_all as launcher_stop_all,
    stop_service,
)

# 馏析队列文件（只读概览）
QUEUE_FILE = Path(r"D:\nigredo\data\queue.json")
UPLOAD_TMP = PROJECT_ROOT / "drop" / "_upload_tmp"
UPLOAD_TMP.mkdir(parents=True, exist_ok=True)


# ────────────────────────────────────────────────────────────
# Tab 1: 周看板
# ────────────────────────────────────────────────────────────
def render_dashboard(container: ui.column) -> None:
    container.clear()
    with container:
        monday, now = week_bounds()
        ui.label(
            f"本周录入一览 · 周一 {monday.strftime('%Y-%m-%d')} ~ 今天 {now.strftime('%Y-%m-%d')}"
            f" ｜ 数据来自 🏭 熔知"
        ).classes("text-sm text-gray-500")
        if not qdrant_reachable():
            ui.label("⚠️ 连不上熔知数据库（Qdrant）。请确认 Qdrant 已启动，并已运行 start_all.bat。")
            return
        docs = fetch_week_docs()
        if not docs:
            ui.label("📭 本周还没有新录入。去 🏭 熔知 添加知识后，这里会自动出现本周卡片。")
            return
        sources: dict = {}
        for d in docs:
            sources.setdefault(d.get("source") or "未知来源", []).append(d)
        ui.label(f"本周新增 {len(docs)} 条 · 来源 {len(sources)} 个").classes("text-lg font-bold")
        with ui.row().classes("flex-wrap"):
            for src, items in sources.items():
                with ui.card().classes("w-64"):
                    ui.label(src).classes("font-bold")
                    ui.label(f"{len(items)} 条")
                    for d in items[:8]:
                        ui.label(f"• {(d.get('title') or '(无标题)')}").classes("text-sm")


# ────────────────────────────────────────────────────────────
# Tab 2: 摄入入口
# ────────────────────────────────────────────────────────────
def _notify_res(res: dict) -> None:
    if res.get("ok"):
        ui.notify(res.get("message", "完成"), type="positive")
    else:
        ui.notify(res.get("message", "失败"), type="negative")


def _on_bilibili(bili_input: ui.input) -> None:
    url = (bili_input.value or "").strip()
    if not url:
        ui.notify("请先贴入地址", type="warning")
        return
    _notify_res(route_bilibili(url))


def _on_upload(e) -> None:
    for f in e:
        try:
            tmp = UPLOAD_TMP / f.name
            tmp.write_bytes(f.content)
            _notify_res(route_file(str(tmp)))
        except Exception as ex:
            ui.notify(f"上传失败：{ex}", type="negative")


def _on_note(note_area: ui.textarea) -> None:
    note = (note_area.value or "").strip()
    if not note:
        ui.notify("笔记为空", type="warning")
        return
    _notify_res(route_note(note))


def render_services(container: ui.column) -> None:
    container.clear()
    with container:
        for name, spec in SERVICES.items():
            running = is_running(name)
            with ui.row().classes("items-center"):
                ui.label(f"{'🟢' if running else '🔴'} {spec['label']}")
                ui.button("启动", on_click=lambda n=name: (start_service(n), render_services(container)))
                ui.button("停止", on_click=lambda n=name: (stop_service(n), render_services(container)))


def render_ingest(container: ui.column) -> None:
    container.clear()
    with container:
        ui.label("① 投递").classes("text-lg font-bold")
        with ui.row().classes("items-end"):
            bili_input = ui.input(
                "B站链接（支持 b23.tv 短链）",
                placeholder="https://www.bilibili.com/video/BV...",
            ).classes("w-96")
            ui.button("🚀 加入馏析队列", on_click=lambda: _on_bilibili(bili_input))
        ui.upload(on_upload=_on_upload, multiple=True).classes("w-full")
        ui.label("支持 md/pdf/txt/png/jpg → 送入熔知收件箱").classes("text-xs")
        note_area = ui.textarea("✏️ 闪念笔记（生成标准 .md 送入熔知收件箱）").classes("w-full")
        ui.button("💾 保存笔记", on_click=lambda: _on_note(note_area))

        ui.separator()
        ui.label("② 三器启停（薄壳 · 不编排流程）").classes("text-lg font-bold")
        ui.label("打开本页不会自动启动任何服务；关闭网页也不会杀掉它们。需手动启动。").classes("text-xs text-gray-500")
        svc_col = ui.column()
        with ui.row():
            ui.button("🚀 一键启动摄入管线", on_click=lambda: (launcher_start_all(), render_services(svc_col)))
            ui.button("🛑 一键停止摄入管线", on_click=lambda: (launcher_stop_all(), render_services(svc_col)))
        render_services(svc_col)

        ui.separator()
        ui.label("③ 馏析队列概览").classes("text-lg font-bold")
        total = pending = processing = 0
        if QUEUE_FILE.exists():
            try:
                items = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
                total = len(items)
                pending = sum(1 for i in items if i.get("status") == "pending")
                processing = sum(1 for i in items if i.get("status") == "processing")
            except Exception:
                pass
        with ui.row():
            ui.label(f"队列总数：{total}")
            ui.label(f"待处理：{pending}")
            ui.label(f"处理中：{processing}")
        ui.label("队列不写 'done' 记录：成功才移除，崩溃不丢项。").classes("text-xs text-gray-500")

        ui.separator()
        ui.label("④ 三器日志").classes("text-lg font-bold")
        for name, spec in SERVICES.items():
            with ui.expansion(f"📜 {spec['label']} 日志"):
                p = LOGS_DIR / f"{name}.log"
                txt = "(无日志：服务未启动或未产生输出)"
                if p.exists():
                    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
                    txt = "\n".join(lines[-200:])
                ui.code(txt)


# ────────────────────────────────────────────────────────────
# Tab 3: 总指挥部
# ────────────────────────────────────────────────────────────
def render_hq(container: ui.column) -> None:
    container.clear()
    with container:
        ui.label("① 服务健康状态").classes("text-lg font-bold")
        for h in check_all():
            if h["online"]:
                extra = f"{h.get('latency_ms')}ms" if h.get("latency_ms") is not None else "在线"
                ui.label(f"✅ {h['project']} — {extra}")
            else:
                ui.label(f"❌ {h['project']} — {h.get('status', 'unknown')}")

        ui.separator()
        ui.label("② GitHub 仓库状态").classes("text-lg font-bold")
        try:
            repo_sum = get_all_repo_summaries()
        except Exception as e:
            repo_sum = {}
            ui.label(f"⚠️ GitHub 读取失败：{e}")
        REPO_ALIAS = {
            "Citrinitas": "🏭 熔知", "Nigredo": "⚗️ 馏析",
            "Albedo": "🔬 炼真", "Rubedo": "✨ 凝华", "OpusMagnum": "⚛️ 巨作",
        }
        for key, alias in REPO_ALIAS.items():
            data = repo_sum.get(key, {})
            if "error" in data:
                ui.label(f"{alias} — ⚠️ GitHub Token 未配置")
            else:
                ui.label(f"{alias} — {data.get('open_issues', 0)} open issues · ⭐ {data.get('stars', 0)}")

        ui.separator()
        ui.label("③ 任务看板（来自 GitHub Issues）").classes("text-lg font-bold")
        try:
            tasks = get_all_tasks(state="open")
        except Exception as e:
            tasks = []
            ui.label(f"⚠️ 任务读取失败：{e}")
        if not tasks:
            ui.label("暂无任务数据。")
        else:
            done = sum(1 for t in tasks if t.get("status") == "done")
            ui.label(f"总任务 {len(tasks)} · 进行中 {len(tasks) - done} · 已完成 {done}")
            for t in tasks[:30]:
                ui.label(f"• [{t.get('project_label', '')}] {t.get('title', '')}")

        ui.separator()
        ui.label("④ API 规范速查（各器需实现的端点）").classes("text-lg font-bold")
        ui.markdown(
            "| 项目 | 端点 | 用途 |\n"
            "|------|------|------|\n"
            "| 🏭 熔知 | GET /health | 健康检查 |\n"
            "| 🏭 熔知 | POST /api/documents/ingest | 入库文档 |\n"
            "| 🏭 熔知 | GET /api/documents/search | 搜索（熔知 API 待实现，巨作暂直读 Qdrant） |\n"
        )

        ui.separator()
        ui.label("⑤ 开发路线").classes("text-lg font-bold")
        ui.markdown(
            "| 阶段 | 项目 | 状态 |\n"
            "|------|------|:--:|\n"
            "| Phase 1 地基 | 🏭 熔知 | ✅ MVP |\n"
            "| Phase 2 摄取 | ⚗️ 馏析 | B站→字幕→文档 |\n"
            "| Phase 3 验证 | 🔬 炼真 | 认知精炼 |\n"
            "| Phase 4 输出 | ✨ 凝华 | 进行中 |\n"
        )


# ────────────────────────────────────────────────────────────
# 页面装配
# ────────────────────────────────────────────────────────────
ui.label("⚛️ OpusMagnum · 巨作 / GreatWork").classes("text-2xl font-bold")
ui.label("一人公司总指挥部 · 周看板 + 摄入入口 + 总指挥部").classes("text-sm text-gray-500")

with ui.tabs() as tabs:
    t_dash = ui.tab("📊 周看板")
    t_ingest = ui.tab("📥 摄入入口")
    t_hq = ui.tab("🎛️ 总指挥部")

with ui.tab_panels(tabs, value=t_dash):
    with ui.tab_panel(t_dash):
        dash_col = ui.column()
        ui.button("🔄 刷新", on_click=lambda: render_dashboard(dash_col))
        render_dashboard(dash_col)
    with ui.tab_panel(t_ingest):
        ingest_col = ui.column()
        render_ingest(ingest_col)
    with ui.tab_panel(t_hq):
        hq_col = ui.column()
        ui.button("🔄 刷新", on_click=lambda: render_hq(hq_col))
        render_hq(hq_col)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=settings.opus_port, title="OpusMagnum · 巨作", reload=False)
