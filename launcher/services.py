"""巨作各服务的启动定义。

路径基于本机固定布局（D:\\nigredo / D:\\albedo / D:\\citrinitas / D:\\rubedo）。
每个服务包含：启动命令、健康检查方式、依赖关系、启动宽限期，以及：
  - color    : 服务/项目的主题色（RGBA），用于托盘图标的彩色方框
  - is_phase : 是否属于「炼金四相」（Nigredo/Albedo/Citrinitas/Rubedo），
               只有 is_phase=True 的才进主图标的 2x2 色块拼图；
               Qdrant 是底层向量库，不属于「项目」，不进主图标。
"""

import os

LAUNCHER_DIR = os.path.dirname(os.path.abspath(__file__))

# 各项目目录（本机固定布局）
NIGREDO_DIR = r"D:\nigredo"
ALBEDO_DIR = r"D:\albedo"
CITRINITAS_DIR = r"D:\citrinitas"
RUBEDO_DIR = r"D:\rubedo"

# 炼金四相主题色（黑化/白化/黄化/红化）+ 总指挥部紫（底层库用）
COLOR_NIGREDO = (43, 43, 43, 255)      # 黑化 → 深黑灰（纯黑看不见，用深灰）
COLOR_ALBEDO = (240, 240, 240, 255)    # 白化 → 白
COLOR_CITRINITAS = (241, 196, 15, 255) # 黄化 → 金黄
COLOR_RUBEDO = (231, 76, 60, 255)      # 红化 → 红
COLOR_OPUS = (155, 89, 182, 255)       # 总指挥部 → 紫（底层库）


def _venv(py_dir: str) -> str:
    return os.path.join(py_dir, "venv", "Scripts", "python.exe")


SERVICES = [
    {
        "key": "qdrant",
        "name": "Qdrant 向量库",
        "ui": "http://127.0.0.1:6333/dashboard",
        "color": COLOR_OPUS,
        "is_phase": False,
        "spawn": {
            "kind": "powershell",
            "cwd": CITRINITAS_DIR,
            "args": [
                "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", os.path.join(CITRINITAS_DIR, "scripts", "qdrant_helper.ps1"),
                "-Action", "start", "-ProjectDir", CITRINITAS_DIR,
            ],
        },
        "health": {"type": "tcp", "host": "127.0.0.1", "port": 6333},
        "depends_on": [],
        "proc_ephemeral": True,   # powershell 拉起 qdrant 后会自行退出，健康只看端口
        "grace": 30,
    },
    {
        "key": "nigredo",
        "name": "馏析 Nigredo（采集）",
        "ui": None,
        "color": COLOR_NIGREDO,
        "is_phase": True,
        "spawn": {
            "kind": "python",
            "cwd": NIGREDO_DIR,
            "python": _venv(NIGREDO_DIR),
            "args": ["run_queue.py"],
        },
        "health": {"type": "lockpid", "lock": os.path.join(NIGREDO_DIR, "data", "queue_consumer.lock")},
        # 启动前额外清理的孤儿锁：queue.lock 是文件锁（与上面的 consumer 锁不同一把），
        # 消费进程被强杀时 finally 不执行会遗留它；不清会在新进程抢锁时超时崩溃 → 重启死循环。
        "bootstrap_locks": [os.path.join(NIGREDO_DIR, "data", "queue.lock")],
        "depends_on": [],
        "grace": 15,
    },
    {
        "key": "albedo",
        "name": "炼真 Albedo（精炼）",
        "ui": None,
        "color": COLOR_ALBEDO,
        "is_phase": True,
        "spawn": {
            "kind": "python",
            "cwd": ALBEDO_DIR,
            "python": _venv(ALBEDO_DIR),
            "args": ["-m", "watcher.run"],
        },
        "health": {"type": "lockpid", "lock": os.path.join(ALBEDO_DIR, ".watcher.pid")},
        "depends_on": ["nigredo"],
        "grace": 15,
    },
    {
        "key": "citrinitas",
        "name": "熔知 Citrinitas（知识库界面）",
        "ui": "http://127.0.0.1:8080",
        "color": COLOR_CITRINITAS,
        "is_phase": True,
        "spawn": {
            "kind": "python",
            "cwd": CITRINITAS_DIR,
            "python": _venv(CITRINITAS_DIR),
            "args": ["main.py"],
        },
        "health": {"type": "citrinitas", "url": "http://127.0.0.1:8080/health"},
        "depends_on": ["qdrant"],
        # 启动前先释放 8080 端口（接管之前手动开的旧实例），与 citrinitas run.bat 一致
        "pre": [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", os.path.join(CITRINITAS_DIR, "scripts", "port_cleanup.ps1"),
            "-Port", "8080",
        ],
        "takeover_lock": os.path.join(CITRINITAS_DIR, "local_data", ".citrinitas.lock"),
        "grace": 60,   # 给熔知 watcher 启动留时间；启动 60s 内不查 watcher.alive
    },
    {
        "key": "rubedo",
        "name": "凝华 Rubedo（SOP 平台）",
        "ui": "http://127.0.0.1:8081",
        "color": COLOR_RUBEDO,
        "is_phase": True,
        "spawn": {
            "kind": "python",
            "cwd": RUBEDO_DIR,
            "python": _venv(RUBEDO_DIR),
            "args": ["app.py"],
        },
        "health": {"type": "tcp", "host": "127.0.0.1", "port": 8081},
        "depends_on": [],
        # 启动前释放 8081 端口（接管之前手动开的旧实例），复用熔知的端口清理脚本
        "pre": [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", os.path.join(CITRINITAS_DIR, "scripts", "port_cleanup.ps1"),
            "-Port", "8081",
        ],
        "grace": 30,
    },
]
