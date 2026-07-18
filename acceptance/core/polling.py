"""轮询辅助：文件夹新文件 + 摄入日志新行。

轮询间隔由调用方按用户裁定传入（炼真 300s / 馏析熔知 60s）。
所有函数只做「读」，不修改任何文件；监控由三器各自的 watcher 自动进行，harness 不另起监控进程。
"""
from __future__ import annotations

import json
import time
from pathlib import Path


def poll_new_file(directory, seen: set, timeout: int, interval: float,
                  pattern: str = "*.md") -> Path | None:
    """轮询 directory，返回首个不在 seen 集合中的新文件路径；发现后加入 seen。

    directory: 被轮询的目录（Path 或 str）
    seen:      已见文件名集合（会被原地更新，避免重复返回同一文件）
    timeout:   最长等待秒数
    interval:  轮询间隔秒数
    pattern:   文件名通配
    """
    directory = Path(directory)
    deadline = time.time() + timeout
    while time.time() < deadline:
        for p in sorted(directory.glob(pattern)):
            if p.is_file() and p.name not in seen:
                seen.add(p.name)
                return p
        time.sleep(interval)
    return None


def poll_ingest_log(log_path, pos_holder: list, timeout: int, interval: float,
                    match_source: str | None = None) -> str | None:
    """轮询 ingest_log.jsonl 新行，返回首个新 doc_id（可过滤 match_source）。

    log_path:    ingest_log.jsonl 路径
    pos_holder:  [已读字节位置] 的列表（原地更新）
    timeout:     最长等待秒数
    interval:    轮询间隔秒数
    match_source:若给定，仅返回 source_file 含该子串的 doc_id（用于精确匹配本次注入的文件）
    """
    log_path = Path(log_path)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if log_path.exists():
            size = log_path.stat().st_size
            if size > pos_holder[0]:
                with log_path.open("r", encoding="utf-8") as f:
                    f.seek(pos_holder[0])
                    new_text = f.read(size - pos_holder[0])
                pos_holder[0] = size
                for line in new_text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    doc_id = rec.get("doc_id") or rec.get("doc_uid")
                    if not doc_id:
                        continue
                    src = rec.get("source_file", "")
                    if match_source and match_source not in src:
                        continue
                    return doc_id
        time.sleep(interval)
    return None
