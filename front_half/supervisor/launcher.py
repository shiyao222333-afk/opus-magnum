"""
巨作摄入入口 — 三器启停 + 日志汇聚（模块 A4 / A5）

设计原则（对齐用户硬约束）：
  - 巨作只做"投递 + 启停 + 看日志"，不编排流程（薄壳）。
  - 关巨作网页不杀三器：子进程用 DETACHED_PROCESS 启动，脱离父进程独立存活。
  - 启动前按端口/PID 去重，绝不双开（防同地址被两进程各处理一次=串）。
  - 日志重定向到 logs/<name>.log，启动前做 5MB 轮转（留最近3），三器内部零改。

服务定义：
  - 有端口的（熔知）：用端口判定存活 + 按端口查 PID 停止。
  - 无端口的（馏析队列消费 / 炼真监控 / 投递箱监听）：用 PID 文件判定存活 + 按 PID 停止。
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

logger = logging.getLogger("opus.launcher")

OPUS_DIR = Path(__file__).resolve().parent.parent.parent  # D:\opus-magnum
ROOT = OPUS_DIR.parent  # D:\
LOGS_DIR = OPUS_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

NIGREDO = ROOT / "nigredo"
ALBEDO = ROOT / "albedo"
CITRINITAS = ROOT / "citrinitas"

LOG_MAX_BYTES = 5 * 1024 * 1024
LOG_KEEP = 3

# 各项目优先用各自 venv 的 python（与 run.bat 行为一致）
def _py(project_dir: Path) -> str:
    v = project_dir / "venv" / "Scripts" / "python.exe"
    return str(v) if v.exists() else "python"


SERVICES = {
    "nigredo_consumer": {
        "label": "⚗️ 馏析队列消费",
        "port": None,
        # 锁文件(data/queue_consumer.lock)由 run_queue.py 自己管理（单消费者防双开），
        # 启动器只"读"它做存活判定，不"写"，避免两个组件抢同一把锁导致消费器误判自杀。
        "pid_file": NIGREDO / "data" / "queue_consumer.lock",
        "launcher_writes_pid": False,
        "cmd": [_py(NIGREDO), str(NIGREDO / "run_queue.py")],
        "cwd": str(NIGREDO),
    },
    "drop_watcher": {
        "label": "📥 AI 投递箱监听",
        "port": None,
        "pid_file": OPUS_DIR / "drop" / "drop_watcher.lock",
        "cmd": [sys.executable, str(OPUS_DIR / "front_half" / "drop_watcher.py")],
        "cwd": str(OPUS_DIR),
    },
    "albedo": {
        "label": "🔬 炼真",
        "port": None,
        "pid_file": ALBEDO / ".watcher.pid",
        "launcher_writes_pid": False,
        "cmd": [str(ALBEDO / "run.bat")],
        "cwd": str(ALBEDO),
    },
    "citrinitas": {
        "label": "🏭 熔知",
        "port": 8080,
        "pid_file": None,
        "cmd": [str(CITRINITAS / "run.bat")],
        "cwd": str(CITRINITAS),
    },
}


# ── 进程存活判定 ────────────────────────────────────────────
def _pid_alive(pid: int) -> bool:
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
                    return ec.value == 259  # STILL_ACTIVE
                return False
            finally:
                kernel32.CloseHandle(handle)
        except Exception:  # noqa: BLE001
            pass
    # 兜底（非 Windows / ctypes 异常）
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


def _port_listening(port: int) -> bool:
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()


def _pid_on_port(port: int) -> int | None:
    """用 PowerShell 查占用端口的 PID（仅 Windows 有效）。"""
    if sys.platform != "win32":
        return None
    ps = (
        "Get-NetTCPConnection -LocalPort %d -State Listen -ErrorAction SilentlyContinue"
        " | Select-Object -ExpandProperty OwningProcess" % port
    )
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        return None
    for line in out.splitlines():
        line = line.strip()
        if line.isdigit():
            return int(line)
    return None


def is_running(name: str) -> bool:
    spec = SERVICES.get(name)
    if not spec:
        return False
    if spec["port"] is not None:
        return _port_listening(spec["port"])
    # 无端口：看 PID 文件
    pf = spec.get("pid_file")
    if pf and pf.exists():
        try:
            pid = int(pf.read_text(encoding="utf-8").strip())
        except (ValueError, OSError):
            return False
        return _pid_alive(pid)
    return False


# ── 日志轮转（A5）──────────────────────────────────────────
def _rotate_log(name: str) -> None:
    log_path = LOGS_DIR / f"{name}.log"
    if not log_path.exists() or log_path.stat().st_size < LOG_MAX_BYTES:
        return
    # 轮转：.log → .1 → .2 → .3（保留最近 3 份）
    for i in range(LOG_KEEP - 1, 0, -1):
        older = LOGS_DIR / f"{name}.log.{i}"
        newer = LOGS_DIR / f"{name}.log.{i - 1}"
        if newer.exists():
            newer.replace(older)
    log_path.replace(LOGS_DIR / f"{name}.log.1")


# ── 启动 / 停止 ─────────────────────────────────────────────
def start_service(name: str) -> str:
    """启动服务。已运行则返回 'already'，否则拉起返回 'started'。"""
    spec = SERVICES.get(name)
    if not spec:
        return f"未知服务: {name}"
    if is_running(name):
        return "already"

    _rotate_log(name)
    log_path = LOGS_DIR / f"{name}.log"
    log_f = open(log_path, "ab", buffering=0)

    kwargs = {
        "cwd": spec["cwd"],
        "stdout": log_f,
        "stderr": log_f,
        "close_fds": True,
    }
    # 脱离父进程，关巨作后仍能独立存活（满足"关巨作不杀三器"）
    if sys.platform == "win32":
        kwargs["creationflags"] = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
    else:
        kwargs["start_new_session"] = True

    try:
        proc = subprocess.Popen(spec["cmd"], **kwargs)
    except Exception as e:  # noqa: BLE001
        log_f.close()
        return f"启动失败: {e}"

    pf = spec.get("pid_file")
    if pf and spec.get("launcher_writes_pid", True):
        pf.parent.mkdir(parents=True, exist_ok=True)
        pf.write_text(str(proc.pid), encoding="utf-8")
    logger.info(f"已启动 {spec['label']} (pid={proc.pid})")
    return "started"


def stop_service(name: str) -> str:
    """停止服务。按 PID 文件或端口查到的 PID 结束进程。"""
    spec = SERVICES.get(name)
    if not spec:
        return f"未知服务: {name}"
    if not is_running(name):
        return "not_running"

    pid = None
    pf = spec.get("pid_file")
    if pf and pf.exists():
        try:
            pid = int(pf.read_text(encoding="utf-8").strip())
        except (ValueError, OSError):
            pid = None
    if pid is None and spec["port"] is not None:
        pid = _pid_on_port(spec["port"])

    if pid is not None and _pid_alive(pid):
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/PID", str(pid), "/F", "/T"],
                    capture_output=True, timeout=10,
                )
            else:
                import signal

                os.kill(pid, signal.SIGTERM)
        except Exception as e:  # noqa: BLE001
            return f"停止失败: {e}"
        # 给一点时间退出
        for _ in range(10):
            if not _pid_alive(pid):
                break
            time.sleep(0.3)
    if pf and pf.exists():
        try:
            pf.unlink()
        except OSError:
            pass
    return "stopped"


def start_all() -> dict:
    return {name: start_service(name) for name in SERVICES}


def stop_all() -> dict:
    return {name: stop_service(name) for name in SERVICES}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("状态:", {n: is_running(n) for n in SERVICES})
