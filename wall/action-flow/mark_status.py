# -*- coding: utf-8 -*-
"""
mark_status.py — 状态管理器（知识→行动回流系统 · 第6类字段管理台）
职责：给知识库文档管理「第6类（使用期手动填）」字段：
  - 行动状态：need_deep（📌需深入）/ done（✅已完成）/ archived（📦归档）
  - 收藏：star / unstar（写熔知 stats.starred）
  - 工作流阶段：lifecycle <六档>（写熔知 lifecycle）
三段行动状态（含归档）只记记账本 state.json，不写熔知——归档是本清单的本地偏好，
每个仪表盘各自管理；熔知搜索默认包含归档（2026-08-04 起）。熔知 is_archived 保留为
历史只读标记，不再由本清单写入。
架构边界：只通过 Qdrant HTTP 交互，不依赖熔知代码路径。

用法：
  python mark_status.py <doc_id> need_deep          # 📌 需深入（只记记账本）
  python mark_status.py <doc_id> done               # ✅ 已完成（只记记账本）
  python mark_status.py <doc_id> archived           # 📦 已归档（只记记账本，不写熔知）
  python mark_status.py <doc_id> unarchive          # 取消归档（清记账本状态）
  python mark_status.py <doc_id> star               # ★ 收藏（写熔知 stats.starred=true + 记账本）
  python mark_status.py <doc_id> unstar             # 取消收藏（写熔知 stats.starred=false + 记账本）
  python mark_status.py <doc_id> lifecycle <阶段>    # 📅 工作流阶段（写熔知 lifecycle；六档见下）
  python mark_status.py --list                      # 列出当前所有状态
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

VALID_STATUS = {"need_deep", "done", "archived", "unarchive", "undone", "unneed_deep"}
# 收藏类状态（熔知侧要写 stats.starred）
STARRED_FLAG = {"star": True, "unstar": False}
# lifecycle 六档（第6类使用期字段，与熔知 classifications.LIFECYCLE_OPTIONS 对齐）
LIFECYCLE_STAGES = ["idea", "draft", "in_progress", "review", "published", "archived"]


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


def set_qdrant_payload(point_ids, payload):
    """写熔知 payload（key-level merge，不碰其他字段）"""
    _http_post(
        f"/collections/{COLLECTION}/points/payload",
        {"payload": payload, "points": point_ids},
    )


def set_qdrant_starred(point_ids, starred, points=None):
    """写熔知 stats.starred（统一 payload 一次写入全部点）

    ⚠️ 实测：本 Qdrant 版本不支持 per-point payload 映射（acknowledged 但静默不写），
    必须用统一 payload + points。stats 为嵌套对象，整体覆盖；access_count 仅在摄入时
    初始化 0、无运行时写入（grep 熔知代码实证），覆盖无损。
    """
    want = bool(starred)
    set_qdrant_payload(point_ids, {"stats": {"access_count": 0, "starred": want}})


def set_qdrant_lifecycle(point_ids, stage):
    """写熔知 lifecycle（顶层 key merge，第6类使用期字段）"""
    set_qdrant_payload(point_ids, {"lifecycle": stage})


def read_back_starred(doc_id):
    """写后读回确认：返回该文档实际 stats.starred 值（任一 chunk 为准）"""
    pts = find_points(doc_id)
    for p in pts:
        if (p.get("payload") or {}).get("stats", {}).get("starred"):
            return True
    return False


def read_back_lifecycle(doc_id):
    """写后读回确认：返回该文档实际 lifecycle 值（非空任一 chunk 为准）"""
    pts = find_points(doc_id)
    for p in pts:
        lc = (p.get("payload") or {}).get("lifecycle")
        if lc:
            return lc
    return ""


def write_backend(doc_id, kind, want, point_ids, points=None):
    """写熔知 + 写后读回确认；失败抛异常。仅 starred / lifecycle 用（归档只记记账本）"""
    if kind == "starred":
        set_qdrant_starred(point_ids, want, points=points)
        time.sleep(0.5)  # Qdrant per-point 写入异步，读回前稍等防读到旧值
        actual = read_back_starred(doc_id)
        if actual != want:
            raise RuntimeError(f"stats.starred 读回校验失败：期望 {want}，实际 {actual}")
        return f"熔知 stats.starred={want}（{len(point_ids)} 块）"
    if kind == "lifecycle":
        set_qdrant_lifecycle(point_ids, want)
        actual = read_back_lifecycle(doc_id)
        if actual != want:
            raise RuntimeError(f"lifecycle 读回校验失败：期望 {want}，实际 {actual}")
        return f"熔知 lifecycle={want}（{len(point_ids)} 块）"
    return ""


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    if args[0] == "--list":
        state = load_state()
        rows = []
        for did, d in state.get("docs", {}).items():
            marks = []
            if d.get("status"):
                marks.append(d["status"])
            if d.get("starred"):
                marks.append("★收藏")
            if d.get("lifecycle"):
                marks.append(f"阶段:{d['lifecycle']}")
            if marks:
                rows.append((",".join(marks), did))
        if not rows:
            print("暂无状态记录")
            return
        for st, did in sorted(rows, key=lambda x: x[0]):
            print(f"{st:<28} | {did}")
        return

    if len(args) < 2:
        print("❌ 用法：mark_status.py <doc_id> <need_deep|done|archived|unarchive|star|unstar|lifecycle>")
        sys.exit(1)

    doc_id, status = args[0], args[1]

    # lifecycle 需要第三个参数（阶段；"" 表示清除还原）
    lifecycle_stage = None
    if status == "lifecycle":
        if len(args) < 3:
            print(f"❌ lifecycle 需要阶段参数：{LIFECYCLE_STAGES}")
            sys.exit(1)
        lifecycle_stage = args[2]
    elif status not in VALID_STATUS and status not in STARRED_FLAG:
        print(f"❌ 无效状态: {status}（可选: need_deep / done / archived / unarchive / star / unstar / lifecycle）")
        sys.exit(1)

    # lifecycle 允许 "" 表示清除还原（写空字符串）
    if status == "lifecycle" and lifecycle_stage == "":
        pass  # 合法：清除
    elif lifecycle_stage is not None and lifecycle_stage not in LIFECYCLE_STAGES:
        print(f"❌ 无效阶段: {lifecycle_stage}（可选: {LIFECYCLE_STAGES}，或空串清除）")
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
    point_ids = [p["id"] for p in points]

    # ── 2. 写熔知（仅 star / lifecycle 需要；三段行动状态含归档只记记账本）──
    # 2026-08-04 起：归档改为清单本地偏好（每个仪表盘各管各的），不再写熔知 is_archived，
    # 熔知搜索默认包含归档。三段状态在记账本是单值字段（need_deep/done/archived 天然互斥），
    # 无需"自动取消归档"分支。
    backend_msg = ""
    try:
        if status in STARRED_FLAG:
            backend_msg = write_backend(doc_id, "starred", STARRED_FLAG[status], point_ids, points=points)
        elif status == "lifecycle":
            backend_msg = write_backend(doc_id, "lifecycle", lifecycle_stage, point_ids)
    except Exception as e:
        print(f"❌ 写熔知失败: {e}")
        sys.exit(1)
    if backend_msg:
        print(f"✅ {backend_msg}")

    # ── 3. 记账本同步（幂等：重复标记同一状态无害）──
    state = load_state()
    docs = state.setdefault("docs", {})
    entry = docs.setdefault(doc_id, {})
    entry["title"] = entry.get("title") or title
    if status in ("unarchive", "undone", "unneed_deep"):
        entry.pop("status", None)
        entry["status_at"] = ""
        labels = {"unarchive": "已取消归档", "undone": "已取消已完成", "unneed_deep": "已取消需深入"}
        print(f"✅ {labels.get(status, '状态已清')}（状态已清）")
    elif status == "unstar":
        entry["starred"] = False
        print("✅ 已取消收藏（熔知 stats.starred=false）")
    elif status == "star":
        entry["starred"] = True
        print("✅ 已收藏（熔知 stats.starred=true）")
    elif status == "lifecycle":
        entry["lifecycle"] = lifecycle_stage
        print(f"✅ 工作流阶段已记：{lifecycle_stage}")
    else:
        entry["status"] = status
        entry["status_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ 状态已记：{status}")
    save_state(state)

    # ── 4. 事件日志 ──
    append_event(
        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] mark_status: {doc_id} → {status}"
        + (f" {lifecycle_stage}" if lifecycle_stage else "")
        + f" ({title[:30]})"
    )
    print(f"标题：{title[:50]}")
    print(f"doc_id：{doc_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 操作失败: {e}", file=sys.stderr)
        sys.exit(1)
