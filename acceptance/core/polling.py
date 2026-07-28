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
                    match_source: str | None = None, seen: set | None = None) -> str | None:
    """轮询 ingest_log.jsonl，返回匹配的新 doc_id（可过滤 match_source）。

    log_path:    ingest_log.jsonl 路径
    pos_holder:  [已读字节位置] 的列表（保留参数，兼容旧调用；本实现改为全量重扫，
                 故该值仅作记录、不再用于增量读取）
    timeout:     最长等待秒数
    interval:    轮询间隔秒数
    match_source:若给定，仅返回 source_file 含该子串的 doc_id（用于精确匹配本次注入的文件）
    seen:        已返回过的 doc_id 集合（原地更新）；传入可避免重复返回同一 doc，
                并在「日志被截断重写」后跳过旧行、命中本轮新行。

    健壮性（修复 L4 验收实测坑，关键）：验收流程每轮记录字段后会调 delete_doc.py
    删测试数据，它会**重写并缩短** ingest_log.jsonl（移除本轮已摄入行）。若用字节
    偏移增量读，下一轮轮询时「文件大小 ≈ 旧偏移」（删行与追平长度恰近似相等）会令
    「size>pos 才读」恒为假 → 完全不读 → 本轮已正常摄入的 doc_id 永不被发现 → 误报超时。

    故本实现**每次轮询全量重扫日志**（验收日志很小，开销可忽略），用 seen 去重、
    返回**最新（最后）**一个匹配行，天然免疫「截断/重写/残留旧行」三类问题。配合
    flow 在 step① 清理 ingest_log 中的 _acc_r 残留行，可彻底避免误命中已删除的旧 doc。
    """
    log_path = Path(log_path)
    if seen is None:
        seen = set()
    deadline = time.time() + timeout
    while time.time() < deadline:
        if log_path.exists():
            text = log_path.read_text(encoding="utf-8")  # 全量重扫：免疫截断/重写
            pos_holder[0] = len(text.encode("utf-8", errors="replace"))
            candidates = []
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                doc_id = rec.get("doc_id") or rec.get("doc_uid")
                if not doc_id or doc_id in seen:
                    continue
                src = rec.get("source_file", "")
                if match_source and match_source not in src:
                    continue
                candidates.append(doc_id)
            if candidates:
                return candidates[-1]  # 最新匹配行，避开残留旧行
        time.sleep(interval)
    return None
