"""
巨作摄入入口 — 三器启停 + 日志汇聚（模块 A4 / A5）

设计原则（对齐用户硬约束）：
  - 巨作只做"投递 + 启停 + 看日志"，不编排流程（薄壳）。
  - 关巨作网页不杀三器：子进程用 DETACHED_PROCESS 启动，脱离父进程独立存活。
  - 启动前按端口/PID 去重，绝不双开（防同地址被两进程各处理一次=串）。
  - 日志重定向到 logs/<name>.log，启动前做 5MB 轮转（留最近3），三器内部零改。

服务清单：统一复用 launcher.services.SERVICES（单一权威清单，list[dict]）。
  本模块只保留"网页端启停 + 存活判定"引擎，数据全部来自 SERVICES，
  不再各自维护一份字典，避免与托盘启动器出现"形状对不上"的坑。
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

logger = logging.getLogger("opus.launcher")

# 单一权威清单：巨作所有服务定义都在 D:\opus-magnum\launcher\services.py。
# 这里直接用文件绝对路径加载它，避免与本项目内的 front_half.supervisor.launcher
# （文件名也叫 launcher）发生包名冲突，也避免改动托盘侧目录结构（它当前可正常用
# 脚本目录相对导入，不动它）。加载出的模块名特意取别名 opus_launcher_services，
# 不占用 launcher 这个名字。
OPUS_DIR = Path(__file__).resolve().parent.parent.parent  # D:\opus-magnum

import importlib.util as _ilu

_SERVICES_FILE = OPUS_DIR / "launcher" / "services.py"
_spec = _ilu.spec_from_file_location("opus_launcher_services", str(_SERVICES_FILE))
_launcher_services = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_launcher_services)
SERVICES = _launcher_services.SERVICES  # 单一权威清单（list[dict]）

ROOT = OPUS_DIR.parent  # D:\
LOGS_DIR = OPUS_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_MAX_BYTES = 5 * 1024 * 1024
LOG_KEEP = 3


def _by_key(name: str) -> dict | None:
    """按 key 在权威清单中查服务（SERVICES 现为 list[dict]）。"""
    for s in SERVICES:
        if s.get("key") == name:
            return s
    return None


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
    spec = _by_key(name)
    if not spec or not spec.get("web_visible"):
        return False
    if spec.get("port") is not None:
        return _port_listening(spec["port"])
    # 无端口：看 PID 文件
    pf = spec.get("pid_file")
    if pf and Path(pf).exists():
        try:
            pid = int(Path(pf).read_text(encoding="utf-8").strip())
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
    spec = _by_key(name)
    if not spec or not spec.get("web_visible"):
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
        Path(pf).parent.mkdir(parents=True, exist_ok=True)
        Path(pf).write_text(str(proc.pid), encoding="utf-8")
    logger.info(f"已启动 {spec.get('label', name)} (pid={proc.pid})")
    return "started"


def stop_service(name: str) -> str:
    """停止服务。按 PID 文件或端口查到的 PID 结束进程。"""
    spec = _by_key(name)
    if not spec or not spec.get("web_visible"):
        return f"未知服务: {name}"
    if not is_running(name):
        return "not_running"

    pid = None
    pf = spec.get("pid_file")
    if pf and Path(pf).exists():
        try:
            pid = int(Path(pf).read_text(encoding="utf-8").strip())
        except (ValueError, OSError):
            pid = None
    if pid is None and spec.get("port") is not None:
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
    if pf and Path(pf).exists():
        try:
            Path(pf).unlink()
        except OSError:
            pass
    return "stopped"


def start_all() -> dict:
    return {s["key"]: start_service(s["key"]) for s in SERVICES if s.get("web_visible")}


def stop_all() -> dict:
    return {s["key"]: stop_service(s["key"]) for s in SERVICES if s.get("web_visible")}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("状态:", {s["key"]: is_running(s["key"]) for s in SERVICES if s.get("web_visible")})
