"""
OpusMagnum · 巨作 / GreatWork — 服务健康检测
定期检测各项目端口，判断在线/离线。

检测策略（健壮版）：
1. 优先调用各项目的 GET /health 端点（Citrinitas 已实现，返回版本等元数据）
2. 若 /health 不存在或超时（Streamlit / NiceGUI 默认不提供该端点），
   则退化为 TCP 端口连通性探测 —— 只要端口在监听即视为在线。
   这样馏析(Streamlit) / 炼真(NiceGUI) 即使没有 /health 也能正确显示在线。
"""

import socket
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from config.settings import settings, ProjectConfig

# 无端口服务的 PID 锁文件（与各自 run.bat / 消费器一致）
# 馏析队列消费：data/queue_consumer.lock（run_queue.py 自管，单消费者）
# 炼真中转监控：.watcher.pid（watcher.run 自管）
_PID_FILES = {
    "Nigredo · 馏析": Path(r"D:\nigredo\data\queue_consumer.lock"),
    "Albedo · 炼真": Path(r"D:\albedo\.watcher.pid"),
}


def _pid_alive(pid: int) -> bool:
    """跨平台进程存活判定（Windows 用 STILL_ACTIVE=259，避免 WinError 87 误判）。"""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
            if handle == 0:
                return False
            try:
                ec = ctypes.c_ulong()
                if kernel32.GetExitCodeProcess(handle, ctypes.byref(ec)):
                    return ec.value == 259
                return False
            finally:
                kernel32.CloseHandle(handle)
        except Exception:  # noqa: BLE001
            pass
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True, timeout=10,
        ).stdout
        if isinstance(out, bytes):
            out = out.decode("utf-8", errors="ignore")
        return str(pid) in out
    except Exception:  # noqa: BLE001
        return False


def _pid_file_alive(pf: Path) -> bool:
    if not pf.exists():
        return False
    try:
        pid = int(pf.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return False
    return _pid_alive(pid)


def _tcp_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """TCP 端口连通性探测：端口在监听即返回 True。"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def check_health(project: ProjectConfig, timeout: float = 2.0) -> dict:
    """
    检测单个项目健康状态。
    优先 GET /health；失败则退化为 TCP 端口探测（兼容 Streamlit / NiceGUI）。
    返回：{"online": bool, "status": str, "project": str, "version": str, "latency_ms": float|None}
    """
    url = project.endpoint("/health")
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "online": True,
                "status": data.get("status", "ok"),
                "project": data.get("project", project.name),
                "version": data.get("version", "unknown"),
                "latency_ms": round(resp.elapsed.total_seconds() * 1000, 1),
            }
        # 非 200（项目未提供 /health）→ 退化到 TCP 探测
    except Exception:
        # 连接失败 / 超时 / 解析错误 → 退化到 TCP 探测
        pass

    # ── 无端口服务：用 PID 锁文件判定存活 ──
    pf = _PID_FILES.get(project.name)
    if pf is not None:
        if _pid_file_alive(pf):
            return {
                "online": True,
                "status": "pid-lock",
                "project": project.name,
                "version": "n/a",
                "latency_ms": None,
            }
        return {"online": False, "status": "offline", "project": project.name}

    # ── 退化策略：TCP 端口探测 ──
    parsed = urlparse(project.url)
    host = parsed.hostname or "localhost"
    port = project.port
    if _tcp_port_open(host, port, timeout=1.0):
        return {
            "online": True,
            "status": "listening",
            "project": project.name,
            "version": "n/a",
            "latency_ms": None,
        }
    return {"online": False, "status": "offline", "project": project.name}


def check_all() -> list:
    """检测所有子项目健康状态。"""
    results = []
    for project in settings.all_projects:
        results.append(check_health(project))
    return results


def format_health_badge(health: dict) -> str:
    """返回 Streamlit 可用的状态徽章文本。"""
    if health["online"]:
        if health.get("latency_ms") is not None:
            return f"✅ **{health['project']}** — 在线（{health['latency_ms']}ms）"
        return f"✅ **{health['project']}** — 在线（端口监听）"
    else:
        return f"❌ **{health['project']}** — {health['status']}"
