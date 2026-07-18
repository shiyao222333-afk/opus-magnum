"""巨作验收流程 CLI。

用法:
    python -m acceptance.cli run --flow bilibili_video --url "https://www.bilibili.com/video/BVxxxx"
    python -m acceptance.cli list

说明:
    - 需以管理员身份运行（与三器一致，因熔知/馏析启动脚本涉及端口清理/提权）。
    - 运行前请确保三器依赖已装（各自 venv），且显卡可用（炼真推理需 GPU）。
    - 本命令只做操作编排，不做审核判定。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from .core.registry import REGISTRY, get_flow
from .flows import bilibili_video  # noqa: F401  (触发 @register 登记，必须在 choices 构建前)


def _stamp(url: str) -> str:
    m = re.search(r"BV\w+", url)
    bv = m.group(0) if m else "video"
    ts = __import__("time").strftime("%Y%m%d_%H%M%S")
    return f"{ts}_{bv}"


def main() -> int:
    ap = argparse.ArgumentParser(prog="acceptance", description="巨作端到端验收流程")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="运行某验收流程")
    p_run.add_argument("--flow", required=True, choices=list(REGISTRY.keys()))
    p_run.add_argument("--url", required=True, help="B站视频网址")
    p_run.add_argument("--out", default=None, help="验收输出目录（默认 acceptance/runs/<stamp>）")

    sub.add_parser("list", help="列出已注册流程")

    args = ap.parse_args()

    if args.cmd == "list":
        print("已注册验收流程:")
        for name in REGISTRY:
            print(f"  - {name}")
        return 0

    if args.cmd == "run":
        flow_cls = get_flow(args.flow)
        out_dir = args.out or str(Path(__file__).resolve().parent / "runs" / _stamp(args.url))
        flow = flow_cls(out_dir)
        res = flow.run(args.url)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res.get("ok") else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
