"""
前半部分总管 — NiceGUI 界面（用户入口）

界面：贴入 B站 链接 → 点「开始」→ 实时显示三段进度（下载字幕/炼真精炼/投递入库）。
后端逻辑在 orchestrator.py（与界面解耦，便于单测与日后替换）。
"""
from nicegui import ui
import threading

from orchestrator import run_pipeline, STAGES

ui.label("前半部分总管 · Opus Magnum").classes("text-2xl font-bold")
ui.label("贴入一个 B站 链接，一键跑完：下载字幕 → 炼真精炼 → 投递入库").classes(
    "text-sm text-gray-500"
)

url_input = ui.input("B站链接", placeholder="https://www.bilibili.com/video/BV...").classes(
    "w-full"
)
log = ui.log().classes("w-full h-64")

# 共享进度队列：worker 线程写，timer 读出来渲染到界面
_progress_q: list = []


def _on_progress(idx, name, status, msg):
    _progress_q.append((idx, name, status, msg))


def _worker(url: str):
    try:
        run_pipeline(url, on_progress=_on_progress)
    except Exception as e:  # noqa: BLE001
        _progress_q.append((-1, "错误", "error", str(e)))


def _refresh():
    if not _progress_q:
        return
    while _progress_q:
        _idx, name, status, msg = _progress_q.pop(0)
        icon = {"start": "▶", "done": "✅", "error": "❌"}.get(status, "•")
        log.push(f"{icon} [{name}] {msg}")


ui.timer(0.3, _refresh)


def _start():
    u = (url_input.value or "").strip()
    if not u:
        log.push("⚠️ 请先贴入 B站 链接")
        return
    _progress_q.clear()
    log.push(f"🚀 启动前半部分流水线：{u}")
    threading.Thread(target=_worker, args=(u,), daemon=True).start()


ui.button("开始", on_click=_start).classes("bg-blue-600 text-white")

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8503, native=True, title="前半部分总管", reload=False)
