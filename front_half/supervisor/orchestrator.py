"""
前半部分总管 — 编排逻辑（与界面解耦，可单独单测）

职责：接收一条 B站 链接，依次跑完三段流水线：
  阶段0 下载字幕  →  (Nigredo 馏析)
  阶段1 炼真精炼  →  (Albedo 炼真)
  阶段2 投递入库  →  (Citrinitas 熔知收件箱，自动入库)

M0 阶段：只把骨架跑通（占位），真实三段调用留作 M2 接入点（见 TODO）。
这样界面可以先做出来，后端逻辑随时替换，互不阻塞。
"""

import os
import sys

# 子项目真实路径（也可走 front_half/ 下的目录联接，效果一样）
NIGREDO_PATH = r"D:\nigredo"
ALBEDO_PATH = r"D:\albedo"
CITRINITAS_INBOX = r"D:\citrinitas\data\inbox"

# 三段流水线名称（界面进度区按此显示）
STAGES = ["下载字幕", "炼真精炼", "投递入库"]


def ensure_subproject_paths():
    """把子项目根目录加进 Python 搜索路径，方便直接 import 它们的模块。"""
    for p in (NIGREDO_PATH, ALBEDO_PATH):
        if os.path.isdir(p) and p not in sys.path:
            sys.path.insert(0, p)


def run_pipeline(bilibili_url: str, on_progress=None):
    """
    跑完整条前半部分流水线。

    on_progress(stage_idx, stage_name, status, message)
        status ∈ {"start", "done", "error"}
    返回 dict：本趟运行的产物摘要（M0 阶段多为占位值）。
    """
    bilibili_url = (bilibili_url or "").strip()
    if not bilibili_url:
        raise ValueError("bilibili_url 不能为空")

    ensure_subproject_paths()
    result = {"url": bilibili_url, "transcript": None, "report_path": None}

    # ── 阶段0：下载字幕（Nigredo 馏析）────────────────────────
    if on_progress:
        on_progress(0, STAGES[0], "start", f"开始处理 {bilibili_url}")
    # TODO(M2)：调用 Nigredo 的下载/字幕模块，拿到结构化文字
    #   from core.downloader import DownloadManager
    #   transcript = DownloadManager().process(bilibili_url)
    transcript = f"[M0 占位] 来自 {bilibili_url} 的字幕/结构化文本"
    result["transcript"] = transcript
    if on_progress:
        on_progress(0, STAGES[0], "done", "字幕就绪（占位，M2 接真实下载）")

    # ── 阶段1：炼真精炼（Albedo 炼真）────────────────────────
    if on_progress:
        on_progress(1, STAGES[1], "start", "送往炼真精炼")
    # TODO(M2)：调用 Albedo 的 refine_text，产出「熔知专用 + 人可读」合体文件
    #   from flows.refine import refine_text
    #   report_path = refine_text(transcript, source_url=bilibili_url)
    result["report_path"] = None
    if on_progress:
        on_progress(1, STAGES[1], "done", "炼真完成（占位，M2 接真实精炼）")

    # ── 阶段2：投递入库（Citrinitas 熔知收件箱）──────────────
    if on_progress:
        on_progress(2, STAGES[2], "start", f"投递到熔知收件箱 {CITRINITAS_INBOX}")
    # TODO(M2)：把阶段1产出的合体文件写入 CITRINITAS_INBOX，熔知监听后自动入库
    #   with open(os.path.join(CITRINITAS_INBOX, os.path.basename(report_path)), "w", encoding="utf-8") as f:
    #       f.write(...)
    if on_progress:
        on_progress(2, STAGES[2], "done", "已投递，熔知将自动入库（占位，M2 接真实投递）")

    return result


if __name__ == "__main__":
    # 命令行冒烟测试（不启动界面）
    def _print(idx, name, status, msg):
        print(f"[{status}] {name}: {msg}")

    out = run_pipeline("https://www.bilibili.com/video/BV1xx411c7mD", on_progress=_print)
    print("结果摘要:", out)
