"""净化子进程环境——移植自 acceptance/core/services.py:_clean_env()。

为什么需要它：WorkBuddy / CodeBuddy 的终端会往环境里塞一批专有变量，其中
ACC_PRODUCT_CONFIG_V3 是一个 300KB+ 的巨型 JSON。一旦被 subprocess 继承进
炼真 / 熔知的子进程，炼真惰性 `import torch` 时会触发原生访问违规（进程直接消失、
没有 Python 报错），导致摄入卡死。拉起子进程前一律剥掉它们，只保留 PATH /
SystemRoot / TEMP / CUDA_* 等运行所需的环境。
"""

import os

_ENV_PREFIXES_TO_STRIP = ("WORKBUDDY_", "CODEBUDDY_", "ACC_")
_ENV_NAMES_TO_STRIP = {
    "CLIENT_INFO_PRODUCT_NAME",
    "NODE_OPTIONS",      # WorkBuddy 注入的 require 钩子，可能干扰子进程
    "PYTHONPATH",        # WorkBuddy 的 shim 目录，会污染子进程 Python 搜索路径
    "MSYSTEM", "MINGW_PREFIX", "MSYS2_PATH", "ORIGINAL_PATH",  # MSYS2 / Git Bash 仿真壳特有
}


def clean_env() -> dict:
    """返回一份剥除 WB 注入变量的干净环境副本，供 subprocess 继承。"""
    return {
        k: v
        for k, v in os.environ.items()
        if not any(k.startswith(p) for p in _ENV_PREFIXES_TO_STRIP)
        and k not in _ENV_NAMES_TO_STRIP
    }
