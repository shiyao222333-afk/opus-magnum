"""健康探活工具：HTTP JSON、TCP 端口、进程 PID 存活、读取锁文件里的 PID。

这些函数都是只读的，用于在总管监控循环里判断"服务还活不活"。
"""

import os
import sys
import socket
import urllib.request
import json

try:
    import ctypes
    _HAS_CTYPES = True
except Exception:  # pragma: no cover
    _HAS_CTYPES = False


def http_get_json(url: str, timeout: float = 5.0):
    """GET 一个返回 JSON 的 URL；失败返回 None。"""
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8", "ignore")
            return json.loads(data)
    except Exception:
        return None


def tcp_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """TCP 端口是否可连通（用于 Qdrant 等无 JSON 接口的服务）。"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def pid_alive(pid: int) -> bool:
    """判断进程是否存活。Windows 上用 OpenProcess + 退出码（259=仍在运行），
    比 os.kill 更准（os.kill 对别的会话进程会误报）。"""
    if not _HAS_CTYPES or sys.platform != "win32":
        try:
            os.kill(pid, 0)
            return True
        except Exception:
            return False
    kernel32 = ctypes.windll.kernel32
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return False
    try:
        ec = ctypes.c_ulong()
        if kernel32.GetExitCodeProcess(handle, ctypes.byref(ec)):
            return ec.value == 259  # STILL_ACTIVE
        return False
    finally:
        kernel32.CloseHandle(handle)


def read_lock_pid(lock_path: str):
    """读取锁文件里的 PID（整数或 None）。"""
    try:
        with open(lock_path, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except Exception:
        return None


def read_lock_json(lock_path: str):
    """读取「角色 + 心跳」锁文件，返回 dict 或 None。

    锁文件格式（新）：
        {"pid": <int>, "role": "<服务 key>", "hb": <unix 时间戳>, "started": <unix 时间戳>}
    兼容旧格式（纯整数 PID）：返回 {"pid": <int>, "role": None, "hb": 0.0}。

    用「角色(role) + 心跳(hb)」而非裸 PID 来判定锁的归属与存活，
    可根治 PID 复用 / SIGKILL 孤儿锁 / 僵尸三类击穿（缺陷 A）。
    """
    try:
        with open(lock_path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        if not raw:
            return None
        try:
            data = json.loads(raw)
            if isinstance(data, dict) and "pid" in data:
                data.setdefault("role", None)
                data.setdefault("hb", 0.0)
                data.setdefault("started", 0.0)
                return data
        except Exception:
            # 旧格式：纯整数 PID
            return {"pid": int(raw), "role": None, "hb": 0.0, "started": 0.0}
    except Exception:
        return None
    return None
