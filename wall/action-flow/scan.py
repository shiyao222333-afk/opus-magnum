# -*- coding: utf-8 -*-
"""
scan.py — 增量扫描员（知识→行动回流系统）
职责：直连 Qdrant 知识库，对比记账本 state.json，输出"新增/变更/未变"清单。
只读不写知识库；跑完向 events.log 追加一条扫描记录。

用法：python scan.py [--json]
  --json 输出机器可读结果（供对话/后续步骤使用）
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
EVENTS_LOG = os.path.join(BASE_DIR, "events.log")
QDRANT_URL = "http://localhost:6333"
COLLECTION = "athanor_v1"


def fetch_all_points():
    """从 Qdrant scroll 全部点（带 payload 不带 vector）"""
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


def aggregate_docs(points):
    """按 doc_id 聚合，计算文档级指纹 + 播放数据 + 归档标记"""
    docs = {}
    for p in points:
        pl = p.get("payload") or {}
        did = pl.get("doc_id") or str(p.get("id"))
        entry = docs.setdefault(
            did, {
                "title": "", "source": "", "chunk_hashes": set(),
                "count": 0, "view_count": 0, "is_archived": False,
            }
        )
        entry["count"] += 1
        if not entry["title"]:
            entry["title"] = pl.get("title") or pl.get("subject") or ""
        if not entry["source"]:
            entry["source"] = pl.get("source") or ""
        # 播放数据（engagement.view_count，取文档内最大值）
        eng = pl.get("engagement") or {}
        if isinstance(eng, dict):
            vc = eng.get("view_count")
            if vc and int(vc) > entry["view_count"]:
                entry["view_count"] = int(vc)
        # 归档标记（任一 chunk 标记归档即文档归档）
        if pl.get("is_archived"):
            entry["is_archived"] = True
        h = pl.get("content_hash")
        if h:
            entry["chunk_hashes"].add(str(h))
    result = {}
    for did, e in docs.items():
        fp_src = f"{e['title']}|{e['source']}|{'|'.join(sorted(e['chunk_hashes']))}"
        result[did] = {
            "title": e["title"],
            "source": e["source"],
            "chunks": e["count"],
            "view_count": e["view_count"],
            "is_archived": e["is_archived"],
            "fingerprint": hashlib.sha256(fp_src.encode("utf-8")).hexdigest()[:16],
        }
    return result


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"version": 1, "docs": {}}
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def append_event(line):
    with open(EVENTS_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="输出机器可读结果")
    args = parser.parse_args()

    points = fetch_all_points()
    live_docs = aggregate_docs(points)

    state = load_state()
    known = state.get("docs", {})

    new_docs, changed_docs, unchanged_docs = [], [], []
    skipped = []  # (did, info, reason) 状态过滤跳过的（不再推荐提炼）
    for did in sorted(live_docs):
        info = live_docs[did]
        st = (known.get(did) or {}).get("status")
        # 状态过滤：熔知已归档 / 记账本已完成 → 不再推荐
        if info["is_archived"]:
            skipped.append((did, info, "已归档"))
            continue
        if st == "done":
            skipped.append((did, info, "已完成"))
            continue
        if did not in known:
            new_docs.append((did, info))
        elif known[did].get("fingerprint") != info["fingerprint"]:
            changed_docs.append((did, info))
        else:
            unchanged_docs.append(did)

    # 需深入 → 置顶推荐（记账本状态 need_deep；排除已归档/已完成，避免重复出现）
    need_deep = [
        (did, info) for did, info in live_docs.items()
        if (known.get(did) or {}).get("status") == "need_deep"
        and not info["is_archived"]
        and (known.get(did) or {}).get("status") != "done"
    ]

    # 记账本里有但库里已不存在的（孤儿记录，保留不删，仅提示）
    orphans = [did for did in known if did not in live_docs]

    result = {
        "scanned_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_docs": len(live_docs),
        "new": [(d, i["title"]) for d, i in new_docs],
        "changed": [(d, i["title"]) for d, i in changed_docs],
        "unchanged": unchanged_docs,
        "orphans": orphans,
        "need_deep": [(d, i["title"]) for d, i in need_deep],
        "skipped": [(d, i["title"], reason) for d, i, reason in skipped],
        # 文档详情（含播放/归档，供提炼时判断推荐权重）
        "docs": {
            did: {
                "title": i["title"],
                "view_count": i["view_count"],
                "is_archived": i["is_archived"],
            }
            for did, i in live_docs.items()
        },
    }

    # 事件日志（每周一条，append-only）
    append_event(
        f"[{result['scanned_at']}] scan: 库内 {result['total_docs']} 份 | "
        f"新增 {len(new_docs)} | 变更 {len(changed_docs)} | 未变 {len(unchanged_docs)} | "
        f"需深入 {len(need_deep)} | 跳过(归档/完成) {len(skipped)} | 孤儿 {len(orphans)}"
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"扫描完成 {result['scanned_at']}")
        print(f"知识库文档数: {result['total_docs']}")
        print(f"🆕 新增 {len(new_docs)}: " + ", ".join(i["title"][:20] for _, i in new_docs[:5]) or "无")
        print(f"✏️  变更 {len(changed_docs)}: " + ", ".join(i["title"][:20] for _, i in changed_docs[:5]) or "无")
        print(f"⏭️  未变(跳过) {len(unchanged_docs)}")
        if need_deep:
            print(f"📌 需深入置顶 {len(need_deep)}: " + ", ".join(i["title"][:20] for _, i in need_deep[:5]))
        if skipped:
            print(f"🚫 跳过(已归档/已完成) {len(skipped)}")
        if orphans:
            print(f"⚠️ 孤儿记录 {len(orphans)}: 记账本有但库里已删")
        print(f"事件日志: {EVENTS_LOG}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 扫描失败: {e}", file=sys.stderr)
        sys.exit(1)
