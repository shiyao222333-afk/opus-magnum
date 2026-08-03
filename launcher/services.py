"""巨作各服务的启动定义（单一权威清单，托盘与网页共用）。

路径基于本机固定布局（D:\\nigredo / D:\\albedo / D:\\citrinitas / D:\\rubedo / D:\\opus-magnum）。
每个服务包含：启动命令、健康检查方式、依赖关系、启动宽限期，以及：
  - color    : 服务/项目的主题色（RGBA），用于托盘图标的彩色方框
  - is_phase : 是否属于「炼金四相」（Nigredo/Albedo/Citrinitas/Rubedo），
              只有 is_phase=True 的才进主图标的 2x2 色块拼图；
              Qdrant 是底层向量库，不属于「项目」，不进主图标。

  - 网页端复用字段（供 front_half/supervisor/launcher.py 做网页内启停 / 存活判定）：
      label               : 人类可读名称
      port                : 有端口的服务用端口判定存活（None 则用 pid_file）
      pid_file            : 无端口服务用 PID 文件判定存活
      cmd                 : 网页端启动命令（列表）
      cwd                 : 启动工作目录
      launcher_writes_pid : 启动器是否负责写 pid_file（默认 True）
      web_visible         : 是否在巨作网页「三器启停」面板中展示（默认 False）

说明：本文件是「一份清单」的唯一定义源。托盘启动器（launcher/launcher.pyw + supervisor.py）
直接读这里的 SERVICES；网页端（front_half/supervisor/launcher.py）也 from launcher.services
import SERVICES。两边只是读取同一份数据，避免再次出现「形状对不上」的坑。
"""

import os

LAUNCHER_DIR = os.path.dirname(os.path.abspath(__file__))

# 各项目目录（本机固定布局）
NIGREDO_DIR = r"D:\nigredo"
ALBEDO_DIR = r"D:\albedo"
CITRINITAS_DIR = r"D:\citrinitas"
RUBEDO_DIR = r"D:\rubedo"
# 巨作总指挥部（NiceGUI 网页，端口由 settings.opus_port 决定，默认 8501）
OPUS_DIR = r"D:\opus-magnum"
OPUS_VENVW = os.path.join(OPUS_DIR, "venv", "Scripts", "pythonw.exe")

# 显示墙 Dashy（Node 项目，D:\opus-magnum\wall\dashy，默认端口 4000）
DASHY_DIR = os.path.join(OPUS_DIR, "wall", "dashy")
# managed node.exe（Dashy engines 要求 ^22.18.0，managed 22.22.2 满足）
NODE_EXE = r"C:\Users\Lenovo\.workbuddy\binaries\node\versions\22.22.2\node.exe"

# B站数据分析（Bili-Insights，D:\opus-magnum\wall\bili-insights，端口 8765 写死 app.py）
BILI_INSIGHTS_DIR = os.path.join(OPUS_DIR, "wall", "bili-insights")

# 炼金四相主题色（黑化/白化/黄化/红化）+ 总指挥部紫（底层库用）
COLOR_NIGREDO = (43, 43, 43, 255)      # 黑化 → 深黑灰（纯黑看不见，用深灰）
COLOR_ALBEDO = (240, 240, 240, 255)    # 白化 → 白
COLOR_CITRINITAS = (241, 196, 15, 255) # 黄化 → 金黄
COLOR_RUBEDO = (231, 76, 60, 255)      # 红化 → 红
COLOR_OPUS = (155, 89, 182, 255)       # 总指挥部 → 紫（底层库）
COLOR_BILI = (251, 114, 153, 255)      # B站数据 → B站粉


def _venv(py_dir: str) -> str:
    return os.path.join(py_dir, "venv", "Scripts", "python.exe")


def _venvw(py_dir: str) -> str:
    """无窗口 Python 解释器（pythonw.exe），用于总管后台启动服务，不出黑框。"""
    return os.path.join(py_dir, "venv", "Scripts", "pythonw.exe")


SERVICES = [
    {
        # ── 托盘字段 ──
        "key": "qdrant",
        "name": "Qdrant 向量库",
        "ui": "http://127.0.0.1:6333/dashboard",
        "color": COLOR_OPUS,
        "is_phase": False,
        "enabled_by_default": True,
        "menu_visible": False,          # Qdrant 是熔知的后端数据库，不单独出现在用户菜单
        # ── 网页端字段 ──
        "web_visible": False,           # 数据库由托盘统管，不在网页「三器启停」面板展示
        "label": "Qdrant 向量库",
        "port": 6333,
        "pid_file": None,
        "cmd": [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", os.path.join(CITRINITAS_DIR, "scripts", "qdrant_helper.ps1"),
            "-Action", "start", "-ProjectDir", CITRINITAS_DIR,
        ],
        "cwd": CITRINITAS_DIR,
        "launcher_writes_pid": False,
        # ── 托盘启动 / 健康 ──
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
        "enabled_by_default": True,
        # ── 网页端字段 ──
        "web_visible": True,
        "label": "⚗️ 馏析队列消费",
        "port": None,
        # 锁文件(data/queue_consumer.lock)由 run_queue.py 自己管理（单消费者防双开），
        # 启动器只"读"它做存活判定，不"写"，避免两个组件抢同一把锁导致消费器误判自杀。
        "pid_file": os.path.join(NIGREDO_DIR, "data", "queue_consumer.lock"),
        # 网页端 cmd 直接用 pythonw 拉起 run_queue.py（与托盘 spawn 一致），
        # 不走 python.exe：避免后台监控器弹出控制台窗口（2026-08-02 修复）。
        "cmd": [_venvw(NIGREDO_DIR), os.path.join(NIGREDO_DIR, "run_queue.py")],
        "cwd": NIGREDO_DIR,
        "launcher_writes_pid": False,
        # ── 托盘启动 / 健康 ──
        "spawn": {
            "kind": "python",
            "cwd": NIGREDO_DIR,
            "python": _venvw(NIGREDO_DIR),
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
        "enabled_by_default": True,
        # ── 网页端字段 ──
        "web_visible": True,
        "label": "🔬 炼真",
        "port": None,
        "pid_file": os.path.join(ALBEDO_DIR, ".watcher.pid"),
        # 网页端 cmd 直接用 pythonw 拉起 watcher.run（与托盘 spawn 一致），
        # 不走 run.bat：run.bat 内部 `start "" python.exe ...` 需新建控制台窗口，
        # 在网页启动的 DETACHED_PROCESS 无控制台上下文里会失败（0xc0000142/拒绝访问），
        # 导致「提示已启动、进程却没起来」。锁文件由 watcher.run 自管，launcher 只读。
        "cmd": [_venvw(ALBEDO_DIR), "-m", "watcher.run"],
        "cwd": ALBEDO_DIR,
        # 锁文件由 albedo 自身管理（run.bat 启动时 [CLEAN] 清理旧 pid，watcher.run 写入
        # JSON 心跳锁）。若 launcher_writes_pid=True，launcher 会把刚 spawn 的 cmd 自身
        # pid 写进 .watcher.pid，run.bat 的 [CLEAN] 读到后 taskkill 自己 → 自杀竞态。
        # 与 nigredo 同款：False（服务自管锁文件，launcher 只读）。2026-08-02 修复。
        "launcher_writes_pid": False,
        # ── 托盘启动 / 健康 ──
        "spawn": {
            "kind": "python",
            "cwd": ALBEDO_DIR,
            "python": _venvw(ALBEDO_DIR),
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
        "enabled_by_default": True,
        # ── 网页端字段 ──
        "web_visible": True,
        "label": "🏭 熔知",
        "port": 8080,
        "pid_file": None,
        # 网页端 cmd 直接用 pythonw 拉起 main.py（与托盘 spawn 一致），
        # 不走 run.bat：run.bat 尾部在无控制台的 DETACHED_PROCESS 上下文里
        # 同样可能触发 0xc0000142（DLL 初始化失败），且 run.bat 会强杀 qdrant.exe、
        # 抢占 8080，网页一键启动不该干这些；单实例锁 main.py 自管。
        "cmd": [_venvw(CITRINITAS_DIR), "main.py"],
        "cwd": CITRINITAS_DIR,
        "launcher_writes_pid": True,
        # ── 托盘启动 / 健康 ──
        "spawn": {
            "kind": "python",
            "cwd": CITRINITAS_DIR,
            "python": _venvw(CITRINITAS_DIR),
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
        "enabled_by_default": False,   # 凝华当前不参与摄入管线，默认不启动
        # ── 网页端字段 ──
        "web_visible": False,
        "label": "凝华 Rubedo（SOP 平台）",
        "port": 8081,
        "pid_file": None,
        "cmd": [os.path.join(RUBEDO_DIR, "run.bat")],
        "cwd": RUBEDO_DIR,
        "launcher_writes_pid": True,
        # ── 托盘启动 / 健康 ──
        "spawn": {
            "kind": "python",
            "cwd": RUBEDO_DIR,
            "python": _venvw(RUBEDO_DIR),
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
    {
        # 巨作总指挥部（NiceGUI 网页，D:\opus-magnum\app.py）
        # 注：旧 launch.bat 里写的 8503 是已删除的旧 Streamlit 版端口；
        # 本版 settings.opus_port 默认 8501（OPUSMAGNUM_PORT 未设时）。
        "key": "opus",
        "name": "巨作入口（总指挥部）",
        "ui": "http://127.0.0.1:8501",
        "color": COLOR_OPUS,
        "is_phase": False,
        "enabled_by_default": True,
        # ── 网页端字段 ──
        "web_visible": False,          # 巨作本身即网页，不在网页内提供「停止巨作」按钮
        "label": "巨作入口（总指挥部）",
        "port": 8501,
        "pid_file": None,
        "cmd": [OPUS_VENVW, os.path.join(OPUS_DIR, "app.py")],
        "cwd": OPUS_DIR,
        "launcher_writes_pid": True,
        # ── 托盘启动 / 健康 ──
        "spawn": {
            "kind": "python",
            "cwd": OPUS_DIR,
            "python": OPUS_VENVW,
            "args": ["app.py"],
        },
        "health": {"type": "citrinitas", "url": "http://127.0.0.1:8501/api/health"},
        "depends_on": ["citrinitas"],
        "grace": 60,    # NiceGUI 冷启动要 ~30s 才绑端口，留足余量
    },
    {
        # AI 投递箱监听：仅由巨作网页管理（托盘不自动启动、不在托盘菜单展示），
        # 故 enabled_by_default / menu_visible 均为 False，仅 web_visible=True。
        "key": "drop_watcher",
        "name": "AI 投递箱监听",
        "ui": None,
        "color": COLOR_OPUS,
        "is_phase": False,
        "enabled_by_default": False,
        "menu_visible": False,
        # ── 网页端字段 ──
        "web_visible": True,
        "label": "📥 AI 投递箱监听",
        "port": None,
        "pid_file": os.path.join(OPUS_DIR, "drop", "drop_watcher.lock"),
        # 网页端 cmd 用 OPUS venv 的 pythonw 拉起（与 albedo/citrinitas 一致），
        # 不依赖 sys.executable：若巨作以 python.exe 启动，sys.executable 会带出控制台窗口。
        "cmd": [_venvw(OPUS_DIR), os.path.join(OPUS_DIR, "front_half", "drop_watcher.py")],
        "cwd": OPUS_DIR,
        "launcher_writes_pid": True,
    },
    {
        # 显示墙 Dashy（成熟聚合仪表盘，Node 项目，D:\opus-magnum\wall\dashy）
        # 关键技巧：spawn.kind=python 的 "python" 字段只是"解释器路径"，
        # 填入 node.exe 即可零改动 supervisor 托管 Node 服务（proc 直接跟踪 node，
        # 停止干净不留孤儿；对比 qdrant 的 powershell ephemeral 更优）。
        # 生产启动 = `node server`（server.js），默认端口 4000（非 Docker 模式）。
        # 2026-08-03 用户拍板：纳入启动器统一管理（托盘/网页可见、死了自动重启）。
        "key": "dashy",
        "name": "显示墙 Dashy（聚合仪表盘）",
        "ui": "http://127.0.0.1:4000",
        "color": COLOR_OPUS,
        "is_phase": False,
        "enabled_by_default": True,      # 显示墙是总入口，跟巨作一起起来
        # ── 网页端字段 ──
        "web_visible": True,
        "label": "🖥️ 显示墙",
        "port": 4000,
        "pid_file": None,
        # 网页端 cmd 用 managed node.exe 拉起 server.js（与托盘 spawn 一致）
        "cmd": [NODE_EXE, "server.js"],
        "cwd": DASHY_DIR,
        "launcher_writes_pid": True,
        # ── 托盘启动 / 健康 ──
        "spawn": {
            "kind": "python",
            "cwd": DASHY_DIR,
            "python": NODE_EXE,
            "args": ["server.js"],
        },
        "health": {"type": "tcp", "host": "127.0.0.1", "port": 4000},
        "depends_on": [],
        "grace": 30,
    },
    {
        # B站数据分析（Bili-Insights，Python/Flask 项目，D:\opus-magnum\wall\bili-insights）
        # 端口 8765 在 app.py 写死（app.run(host="0.0.0.0", port=8765)）。
        # 配置 config.py：BILI_COOKIE 来自 nigredo yt-dlp --cookies-from-browser firefox 导出
        # （2026-08-03，本地注入，绝不外传）；MY_MID=2925080（用户 UID）。
        # 快照：venv python snapshot_job.py（每日，后续挂定时任务）。
        "key": "bili_insights",
        "name": "B站数据（Bili-Insights）",
        "ui": "http://127.0.0.1:8765",
        "color": COLOR_BILI,
        "is_phase": False,
        "enabled_by_default": True,      # 显示墙的 B站数据分区，随托盘一起起来
        # ── 网页端字段 ──
        "web_visible": True,
        "label": "📈 B站数据",
        "port": 8765,
        "pid_file": None,
        "cmd": [_venvw(BILI_INSIGHTS_DIR), "app.py"],
        "cwd": BILI_INSIGHTS_DIR,
        "launcher_writes_pid": True,
        # ── 托盘启动 / 健康 ──
        "spawn": {
            "kind": "python",
            "cwd": BILI_INSIGHTS_DIR,
            "python": _venvw(BILI_INSIGHTS_DIR),
            "args": ["app.py"],
        },
        "health": {"type": "tcp", "host": "127.0.0.1", "port": 8765},
        # 启动前释放 8765 端口（接管之前手动开的旧实例），复用熔知的端口清理脚本
        "pre": [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", os.path.join(CITRINITAS_DIR, "scripts", "port_cleanup.ps1"),
            "-Port", "8765",
        ],
        "depends_on": [],
        "grace": 30,
    },
    {
        # 行动清单陈列架（知识→行动回流系统，D:\opus-magnum\wall\action-flow）
        # 极简 md→HTML 渲染服务（serve.py），读 weekly/ 最新清单，端口 5100。
        # 模板固定只换内容：每周只更新 weekly/*.md，代码永不改动。
        # Dashy 行动清单分区卡片 target=workspace 内嵌本服务。
        "key": "action_flow",
        "name": "行动清单（知识→行动）",
        "ui": "http://127.0.0.1:5100",
        "color": COLOR_OPUS,
        "is_phase": False,
        "enabled_by_default": True,      # 随托盘一起起来，行动清单常驻可看
        # ── 网页端字段 ──
        "web_visible": True,
        "label": "📋 行动清单",
        "port": 5100,
        "pid_file": None,
        "cmd": [_venvw(OPUS_DIR), os.path.join(OPUS_DIR, "wall", "action-flow", "serve.py"), "--port", "5100"],
        "cwd": os.path.join(OPUS_DIR, "wall", "action-flow"),
        "launcher_writes_pid": True,
        # ── 托盘启动 / 健康 ──
        "spawn": {
            "kind": "python",
            "cwd": os.path.join(OPUS_DIR, "wall", "action-flow"),
            "python": _venvw(OPUS_DIR),
            "args": ["serve.py", "--port", "5100"],
        },
        "health": {"type": "tcp", "host": "127.0.0.1", "port": 5100},
        # 启动前释放 5100 端口（接管之前手动开的旧实例，防重启失败循环），复用熔知的端口清理脚本
        "pre": [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", os.path.join(CITRINITAS_DIR, "scripts", "port_cleanup.ps1"),
            "-Port", "5100",
        ],
        "depends_on": [],
        "grace": 30,
    },
]
