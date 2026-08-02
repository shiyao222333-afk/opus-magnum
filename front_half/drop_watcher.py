"""
巨作摄入入口 — AI 投递箱（模块 A2）

轮询 D:/opus-magnum/drop/inbox_drop/*.json，捡到 → 调 route() → 立即删 json。
  - 坏 json：移走（drop/inbox_drop/_bad/）不阻塞后续
  - 单线程顺序处理（按文件名排序），天然防串
  - 捡到即删（无残留）

未来用法：AI 在对话中拿到 B站 地址后，写一个 json 到这里，
本监听进程会自动捡走并处理（等价于网页入口提交）。

⚠️ AI 投递的正规方式 = 往 drop/inbox_drop/ 写 json，投递箱自动捡走交巨作路由；
禁止绕过投递箱直写熔知收件箱或馏析队列。
"""
from __future__ import annotations

import json
import logging
import shutil
import sys
import time
from pathlib import Path

logger = logging.getLogger("opus.drop_watcher")

# 让本模块被独立运行/导入时，能找到同目录的 ingest_router
_THIS = Path(__file__).resolve().parent
if str(_THIS) not in sys.path:
    sys.path.insert(0, str(_THIS))

DROP_DIR = Path(r"D:\opus-magnum\drop\inbox_drop")
BAD_DIR = DROP_DIR / "_bad"


def process_once() -> list:
    """扫描一次投递箱，返回本次处理结果列表。供定时任务/测试调用。"""
    if not DROP_DIR.exists():
        return []
    results = []
    # 仅处理 .json，按文件名排序保证顺序确定（防串）
    files = sorted(
        p for p in DROP_DIR.iterdir() if p.is_file() and p.suffix.lower() == ".json"
    )
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            # 坏 json：移走不阻塞
            BAD_DIR.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(f), str(BAD_DIR / f.name))
                moved = True
            except Exception:  # noqa: BLE001
                moved = False
            msg = f"坏 json，已移走: {e}" if moved else f"坏 json 且移动失败: {e}"
            logger.warning(f"{f.name} {msg}")
            results.append({"file": f.name, "ok": False, "message": msg})
            continue

        # 正常处理
        try:
            from ingest_router import route

            res = route(data)
        except Exception as e:  # noqa: BLE001
            logger.error(f"处理 {f.name} 异常: {e}")
            res = {"ok": False, "kind": "error", "message": str(e)}

        # 不论成功失败，捡到即删（无残留）
        try:
            f.unlink()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"删除 {f.name} 失败: {e}")
        results.append({"file": f.name, **res})
    return results


def run_loop(interval: float = 3.0) -> None:
    """常驻轮询（被巨作后台进程调用）。"""
    logger.info(f"AI 投递箱轮询启动，目录={DROP_DIR}，间隔={interval}s")
    while True:
        try:
            hits = process_once()
            for h in hits:
                logger.info(f"[{'OK' if h.get('ok') else 'FAIL'}] {h.get('file')}: {h.get('message')}")
        except Exception as e:  # noqa: BLE001
            logger.error(f"投递箱轮询异常: {e}")
        time.sleep(interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_loop()
