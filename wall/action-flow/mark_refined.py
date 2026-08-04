# -*- coding: utf-8 -*-
"""
mark_refined.py — 提炼标记器（知识→行动回流系统 · 增量闭环）
职责：把「已提炼成行动项」的文档标记进记账本（写 fingerprint + refined 标记），
     让 scan.py 下次不再把它们当"新增"重复提炼。这是每周更新流程的第 3 步
     （scan 出 new → 提炼成行动项 → 本工具标记已提炼）。

用法：
  python mark_refined.py <doc_id> [doc_id ...]   # 标记指定文档已提炼
  python mark_refined.py --new                   # 标记 scan 报出的全部 new 为已提炼
  python mark_refined.py --list                  # 列出库里存在但未标记的文档
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")
QDRANT_URL = "http://localhost:6333"
COLLECTION = "athanor_v1"


def fetch_all_points():
    """从 Qdrant scroll 全部点（复用 scan 逻辑）"""
    points = []
    offset = None
    while True:
        body = {"limit": 1000, "with_payload": True, "with_vector": False}
        if offset:
            body["offset"] = offset
        req = urllib.request.Request(
            QDRANT_URL + f"/collections/{COLLECTION}/points/scroll",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        batch = data["result"]["points"]
        points.extend(batch)
        next_offset = data["result"].get("next_page_offset")
        if not next_offset or not batch:
            break
        offset = next_offset
    return points


def compute_fingerprint(pl):
    """单文档指纹（与 scan.aggregate_docs 同规则）"""
    title = pl.get("title") or pl.get("subject") or ""
    source = pl.get("source") or ""
    h = pl.get("content_hash")
    return hashlib.sha256(f"{title}|{source}|{h}".encode("utf-8")).hexdigest()[:16]


def live_fingerprints():
    """返回 {doc_id: {"title", "fingerprint"}}（按 doc_id 聚合，chunk 取第一个）"""
    points = fetch_all_points()
    docs = {}
    for p in points:
        pl = p.get("payload") or {}
        did = pl.get("doc_id") or str(p.get("id"))
        if did not in docs:
            docs[did] = {
                "title": pl.get("title") or pl.get("subject") or "",
                "fingerprint": compute_fingerprint(pl),
            }
    return docs


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"version": 1, "docs": {}}
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def mark(doc_ids, live):
    state = load_state()
    docs = state.setdefault("docs", {})
    marked = []
    for did in doc_ids:
        if did not in live:
            print(f"⚠️ 跳过（库里不存在）: {did}")
            continue
        info = live[did]
        entry = docs.setdefault(did, {})
        entry["title"] = entry.get("title") or info["title"]
        entry["fingerprint"] = info["fingerprint"]
        entry["refined"] = True
        entry["refined_week"] = time.strftime("%YW%V")
        entry["refined_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        marked.append(did)
    save_state(state)
    return marked


def main():
    parser = argparse.ArgumentParser(description="标记文档已提炼（增量闭环第 3 步）")
    parser.add_argument("doc_ids", nargs="*", help="要标记的 doc_id")
    parser.add_argument("--new", action="store_true", help="标记 scan 报出的全部 new")
    parser.add_argument("--list", action="store_true", help="列出库里存在但未标记的文档")
    args = parser.parse_args()

    live = live_fingerprints()

    if args.list:
        state = load_state()
        known = state.get("docs", {})
        unmarked = [did for did in live if not (known.get(did) or {}).get("refined")]
        print(f"库内 {len(live)} 份 | 已标记 {len(live) - len(unmarked)} | 未标记 {len(unmarked)}:")
        for did in sorted(unmarked):
            print(f"  {did} | {live[did]['title'][:45]}")
        return

    if args.new:
        state = load_state()
        known = state.get("docs", {})
        target = [did for did in live if not (known.get(did) or {}).get("refined")]
    else:
        target = args.doc_ids
    if not target:
        print("✅ 没有需要标记的文档（全部已提炼）")
        return

    marked = mark(target, live)
    print(f"✅ 已标记 {len(marked)} 条为已提炼（refined_week={time.strftime('%YW%V')}）")
    for did in marked[:10]:
        print(f"  - {did} | {live[did]['title'][:40]}")
    if len(marked) > 10:
        print(f"  ... 等共 {len(marked)} 条")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 失败: {e}", file=sys.stderr)
        sys.exit(1)
