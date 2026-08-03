# -*- coding: utf-8 -*-
"""
mark_status.py — 状态管理器（知识→行动回流系统）
职责：给知识库文档标记状态（需深入 / 已完成 / 已归档），
      归档状态同步写熔知 is_archived 字段（检索时直接排除），
      其余状态记在记账本 state.json（行动系统内部状态）。
架构边界：只通过 Qdrant HTTP 交互，不依赖熔知代码路径。

用法：
  python mark_status.py <doc_id> need_deep    # 📌 需深入（只记记账本）
  python mark_status.py <doc_id> done         # ✅ 已完成（只记记账本）
  python mark_status.py <doc_id> archived     # 📦 已归档（写熔知 is_archived=true + 记账本）
  python mark_status.py <doc_id> unarchive    # 取消归档（写熔知 is_archived=false + 记账本清状态）
  python mark_status.py --list                # 列出当前所有状态
"""
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

VALID_STATUS = {"need_deep", "done", "archived", "unarchive"}
# 归档类状态（熔知侧要写 is_archived）
ARCHIVED_FLAG = {"archived": True, "unarchive": False}


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


def _http_post(path, body):
    req = urllib.request.Request(
        QDRANT_URL + path,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def find_points(doc_id):
    """按 doc_id 查所有点；文档不存在返回 []"""
    data = _http_post(
        f"/collections/{COLLECTION}/points/scroll",
        {
            "filter": {"must": [{"key": "doc_id", "match": {"value": doc_id}}]},
            "limit": 1000,
            "with_payload": True,
            "with_vector": False,
        },
    )
    return data["result"]["points"]


def get_doc_title(points):
    for p in points:
        t = (p.get("payload") or {}).get("title")
        if t:
            return t
    return ""


def set_qdrant_archived(point_ids, archived):
    """写熔知 is_archived（key-level merge，不碰其他字段）"""
    _http_post(
        f"/collections/{COLLECTION}/points/payload",
        {"payload": {"is_archived": bool(archived)}, "points": point_ids},
    )


def read_back_archived(doc_id):
    """写后读回确认：返回该文档实际 is_archived 值（任一 chunk 为准）"""
    pts = find_points(doc_id)
    for p in pts:
        if (p.get("payload") or {}).get("is_archived"):
            return True
    return False


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    if args[0] == "--list":
        state = load_state()
        rows = [(did, d.get("status", "未动")) for did, d in state.get("docs", {}).items() if d.get("status")]
        if not rows:
            print("暂无状态记录")
            return
        for did, st in sorted(rows, key=lambda x: x[1]):
            print(f"{st:>10} | {did}")
        return

    if len(args) < 2:
        print("❌ 用法：mark_status.py <doc_id> <need_deep|done|archived|unarchive>")
        sys.exit(1)

    doc_id, status = args[0], args[1]
    if status not in VALID_STATUS:
        print(f"❌ 无效状态: {status}（可选: need_deep / done / archived / unarchive）")
        sys.exit(1)

    # ── 1. 查文档是否存在（不存在直接报错，不静默成功）──
    try:
        points = find_points(doc_id)
    except Exception as e:
        print(f"❌ Qdrant 连接失败: {e}")
        sys.exit(1)
    if not points:
        print(f"❌ 未找到 doc_id={doc_id} 的记录（知识库中不存在）")
        sys.exit(1)
    title = get_doc_title(points)

    # ── 2. 写熔知 is_archived（仅 archived/unarchive 需要）──
    if status in ARCHIVED_FLAG:
        want = ARCHIVED_FLAG[status]
        point_ids = [p["id"] for p in points]
        try:
            set_qdrant_archived(point_ids, want)
        except Exception as e:
            print(f"❌ 写熔知 is_archived 失败: {e}")
            sys.exit(1)
        # 写后读回确认（防静默失败）
        actual = read_back_archived(doc_id)
        if actual != want:
            print(f"❌ 读回校验失败：期望 is_archived={want}，实际={actual}")
            sys.exit(1)
        print(f"✅ 熔知 is_archived={want} 已写并读回确认（{len(point_ids)} 块）")

    # ── 3. 记账本同步状态（幂等：重复标记同一状态无害）──
    state = load_state()
    docs = state.setdefault("docs", {})
    entry = docs.setdefault(doc_id, {})
    entry["title"] = entry.get("title") or title
    if status == "unarchive":
        entry.pop("status", None)
        entry["status_at"] = ""
        print(f"✅ 已取消归档（熔知 is_archived=false，记账本状态已清）")
    else:
        entry["status"] = status
        entry["status_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ 状态已记：{status} | {title[:40]}")
    save_state(state)

    # ── 4. 事件日志 ──
    append_event(
        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] mark_status: {doc_id} → {status} ({title[:30]})"
    )
    print(f"标题：{title[:50]}")
    print(f"doc_id：{doc_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 操作失败: {e}", file=sys.stderr)
        sys.exit(1)
