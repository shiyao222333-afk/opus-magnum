"""验收 harness 服务编排：拉起 / 探活 / 停止三器，以及喂入馏析。

原则（用户裁定）：
  - harness 只负责启动服务 + 喂输入 + 读输出 + 清理，不干涉三器内部逻辑。
  - 拉起炼真 / 熔知时带验收开关环境变量（ALBEDO_KEEP_INPUT / KB_KEEP_INBOX），
    平时不带 → 原行为恢复。这是「开关式」，不是运行时热切。
  - 轮询间隔按用户裁定：炼真慢 → 5min；馏析 / 熔知快 → 1min。
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

# ── 三器项目根（可用环境变量覆盖，便于不同机器）──
NIGREDO = Path(os.getenv("NIGREDO_ROOT", r"D:\nigredo"))
ALBEDO = Path(os.getenv("ALBEDO_ROOT", r"D:\albedo"))
CITRINITAS = Path(os.getenv("CITRINITAS_ROOT", r"D:\citrinitas"))

# 端口（探活用）
PORTS = {"nigredo": 8502, "albedo": 8501, "citrinitas": 8080}

# 两个监控文件夹（用户定义的「两个监控文件夹」）
WATCH_DIR = Path(os.getenv("ALBEDO_WATCH_DIR", r"D:\opus-magnum\front_half\transit\nigredo_out"))
INBOX_DIR = Path(os.getenv("KB_INBOX_DIR", r"D:\citrinitas\library\inbox"))
INGEST_LOG = CITRINITAS / "local_data" / "ingest_log.jsonl"


def find_python(project: Path) -> str:
    """优先项目 venv，其次受管 venv，最后 PATH python。"""
    cand = project / "venv" / "Scripts" / "python.exe"
    if cand.exists():
        return str(cand)
    managed = Path(r"C:\Users\Lenovo\.workbuddy\binaries\python\envs\default\Scripts\python.exe")
    if managed.exists():
        return str(managed)
    return "python"


class Service:
    """后台子进程句柄。"""

    def __init__(self, name: str, proc: subprocess.Popen):
        self.name = name
        self.proc = proc

    @property
    def alive(self) -> bool:
        return self.proc.poll() is None

    def stop(self, timeout: int = 10) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=timeout)
            except Exception:
                self.proc.kill()


def wait_port(port: int, timeout: int = 120, interval: float = 1.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=2):
                return True
        except OSError:
            time.sleep(interval)
    return False


def ensure_qdrant(timeout: int = 60) -> bool:
    """确保 Qdrant 在 6333 就绪；不在则尝试用 citrinitas 的 helper 启动。"""
    if wait_port(6333, timeout=5):
        return True
    helper = CITRINITAS / "scripts" / "qdrant_helper.ps1"
    if helper.exists():
        try:
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(helper)],
                cwd=str(CITRINITAS), timeout=timeout, check=False,
            )
        except Exception as e:  # pragma: no cover
            print(f"[warn] 启动 Qdrant 失败: {e}", file=sys.stderr)
    return wait_port(6333, timeout=timeout)


def start_albedo() -> Service:
    """拉起炼真监控（带验收开关 ALBEDO_KEEP_INPUT=1）。

    强制 ALBEDO_REQUIRE_HUMAN_REVIEW=false：验收期间中转②必须直接落进收件箱根目录，
    否则会进 review_pending/ 导致熔知不摄入、流程卡死。
    """
    py = find_python(ALBEDO)
    env = dict(os.environ, ALBEDO_KEEP_INPUT="1", ALBEDO_REQUIRE_HUMAN_REVIEW="false")
    proc = subprocess.Popen(
        [py, "-m", "watcher.run"], cwd=str(ALBEDO), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    return Service("albedo", proc)


def start_citrinitas() -> Service:
    """确保 Qdrant 就绪并拉起熔知（带验收开关 KB_KEEP_INBOX=1），探活 8080。"""
    ensure_qdrant()
    py = find_python(CITRINITAS)
    env = dict(os.environ, KB_KEEP_INBOX="1")
    proc = subprocess.Popen(
        [py, "main.py"], cwd=str(CITRINITAS), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    if not wait_port(PORTS["citrinitas"], timeout=120):
        proc.terminate()
        raise RuntimeError("熔知启动超时（端口 8080 未就绪）")
    return Service("citrinitas", proc)


def start_nigredo_ui() -> Service | None:
    """可选：拉起馏析 Streamlit UI（端口 8502）作探活；失败不阻断（处理走 run_queue.py）。"""
    run_bat = NIGREDO / "run.bat"
    if not run_bat.exists():
        return None
    try:
        proc = subprocess.Popen(
            ["cmd", "/c", str(run_bat)], cwd=str(NIGREDO),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return Service("nigredo", proc)
    except Exception as e:  # pragma: no cover
        print(f"[warn] 馏析 UI 启动失败（不影响处理）: {e}", file=sys.stderr)
        return None


def enqueue_nigredo(url: str) -> None:
    """把 URL 写入馏析队列 data/queue.json（去重）。"""
    queue = NIGREDO / "data" / "queue.json"
    items: list = []
    if queue.exists():
        try:
            data = json.loads(queue.read_text(encoding="utf-8"))
            if isinstance(data, list):
                items = data
        except Exception:
            items = []
    if url not in items:
        items.append(url)
    queue.parent.mkdir(parents=True, exist_ok=True)
    queue.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def run_nigredo(url: str, timeout: int = 1800) -> Path:
    """喂入 URL 并运行 run_queue.py 处理，返回新产出的中转①路径（在 WATCH_DIR）。"""
    enqueue_nigredo(url)
    before = {p.name for p in WATCH_DIR.glob("*.md")}
    py = find_python(NIGREDO)
    proc = subprocess.run(
        [py, "run_queue.py"], cwd=str(NIGREDO), timeout=timeout,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"馏析 run_queue.py 失败 (rc={proc.returncode})")
    after = [p for p in WATCH_DIR.glob("*.md") if p.name not in before]
    if not after:
        raise RuntimeError("馏析未产出中转①（WATCH_DIR 无新 .md）")
    after.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return after[0]
