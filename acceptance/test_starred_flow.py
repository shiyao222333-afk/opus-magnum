"""T03 独立验收测试 — 看板收藏持久化（stats.starred，走法 A）· QA 严过关版。

运行（在 D:/opus-magnum 下）：
    C:/Users/Lenovo/.workbuddy/binaries/python/versions/3.13.12/python.exe acceptance/test_starred_flow.py

验收项（对照 docs/plan-dashboard-links-favorites.md §5 T03 + 验收铁律）：
  ① 全 chunk starred 一致（打印真实 stats 字典，不只报状态码）；
  ② access_count 未丢（写前/写后逐 chunk 打印 stats 原文对比）；
  ③ 幂等重复写（同值连写两次均 ok=True）；
  ④ 不存在 doc_id 返 ok=False 且 updated=0；
  ⑤ 跨周收藏能被 fetch_dashboard_docs()["starred"] 捞到（打印 week/starred 实际 doc_id 列表）；
  ⑥ 瞬态标记 _starred/_this_week 严禁回写 Qdrant（写后原始 payload 不含下划线键）；
  ⑦ 边界：is_starred 三层容错 / fetch_dashboard_docs 空集合不崩 / Qdrant 离线或写阶段异常 → ok=False 不抛；
  ⑧ 生产集合 athanor_v1 零污染：测试前后 doc_id 集合 + stats 原文快照逐项对比。

安全：全程在临时集合 _qa_test_tmp（+ _qa_test_empty）上跑，finally 里 DELETE；
生产集合通过 REST 直读快照比对验证未被触碰。
"""
from __future__ import annotations

import datetime
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

TMP = "_qa_test_tmp"
TMP_EMPTY = "_qa_test_empty"
PROD = "athanor_v1"
QDRANT_URL = "http://127.0.0.1:6333"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

FAILURES: list[str] = []


def rest(method: str, path: str, body: dict | None = None, timeout: int = 15) -> dict:
    """直连 Qdrant REST（不经桥模块，用于造数/快照生产集合）。"""
    url = f"{QDRANT_URL}/{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check(name: str, cond: bool, detail: str = "") -> None:
    mark = "✅" if cond else "❌"
    print(f"{mark} {name}" + (f"\n      └─ {detail}" if detail else ""))
    if not cond:
        FAILURES.append(name)


def snapshot_prod() -> dict:
    """REST 直读生产集合，返回 {doc_id: stats} 快照（doc_id 集合 + stats 原文）。"""
    out: dict = {}
    offset = None
    while True:
        body = {"with_payload": True, "with_vector": False, "limit": 100}
        if offset is not None:
            body["offset"] = offset
        res = rest("POST", f"collections/{PROD}/points/scroll", body)
        pts = (res.get("result") or {}).get("points") or []
        for p in pts:
            pl = p.get("payload") or {}
            did = pl.get("doc_id")
            if did is not None:
                out.setdefault(did, pl.get("stats"))
        if not pts or len(pts) < 100:
            break
        nxt = (res.get("result") or {}).get("next_page_offset")
        offset = nxt if nxt is not None else pts[-1].get("id")
    return out


def main() -> int:
    # ── 0. Qdrant 在线探测 ───────────────────────────────────────
    try:
        rest("GET", "collections")
        print("ℹ️  Qdrant 在线（127.0.0.1:6333）")
    except Exception as e:  # noqa: BLE001
        print(f"❌ Qdrant 不可达：{e} —— 验收无法进行（不静默跳过）")
        return 1

    # ── 0.5 生产集合快照（测试前）───────────────────────────────
    prod_before = snapshot_prod()
    print(f"ℹ️  生产集合 {PROD} 快照：{len(prod_before)} 个 doc_id")

    # ── 1. 建临时集合 ────────────────────────────────────────────
    rest("DELETE", f"collections/{TMP}")
    rest("DELETE", f"collections/{TMP_EMPTY}")
    created = rest("PUT", f"collections/{TMP}", {"vectors": {"size": 4, "distance": "Cosine"}})
    if not created.get("result"):
        print(f"❌ 建临时集合失败: {created}")
        return 1
    rest("PUT", f"collections/{TMP_EMPTY}", {"vectors": {"size": 4, "distance": "Cosine"}})

    try:
        # ── 2. 造数：D1=2 chunk 上周录入（跨周收藏场景）；D2=1 chunk 本周 ──
        last_week = (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat()
        this_week = datetime.datetime.now().isoformat()
        points = [
            {"id": 1, "vector": [0.1, 0.2, 0.3, 0.4],
             "payload": {"doc_id": "D1", "title": "跨周收藏文档", "text": "正文一",
                         "source": "s1.md", "source_project": "proj-a",
                         "stats": {"access_count": 7, "starred": False},
                         "timeline": {"ingested": last_week}}},
            {"id": 2, "vector": [0.5, 0.6, 0.7, 0.8],
             "payload": {"doc_id": "D1", "title": "跨周收藏文档", "text": "正文二",
                         "source": "s1.md", "source_project": "proj-a",
                         "stats": {"access_count": 7, "starred": False},
                         "timeline": {"ingested": last_week}}},
            {"id": 3, "vector": [0.9, 1.0, 1.1, 1.2],
             "payload": {"doc_id": "D2", "title": "本周新文档", "text": "正文",
                         "source": "s2.md", "source_project": "proj-b",
                         "stats": {"access_count": 3, "starred": False},
                         "timeline": {"ingested": this_week}}},
        ]
        up = rest("PUT", f"collections/{TMP}/points?wait=true", {"points": points})
        check("造数完成（D1×2 chunk + D2×1 chunk）", up.get("result", {}).get("status") == "completed",
              str(up.get("result")))

        # ── 3. 以临时集合导入桥模块（env 必须在 import 前设置）──
        os.environ["QDRANT_COLLECTION"] = TMP
        sys.path.insert(0, str(PROJECT_ROOT))
        from core import qdrant_bridge as qb  # noqa: E402
        qb.QDRANT_COLLECTION = TMP  # 双保险：显式钉死集合名
        qb.QDRANT_URL = QDRANT_URL
        check("桥模块指向临时集合", qb.QDRANT_COLLECTION == TMP,
              f"QDRANT_COLLECTION={qb.QDRANT_COLLECTION}")

        before = [p for p in qb.scroll_payloads() if p["doc_id"] == "D1"]
        print("  写前 D1 stats 原文:", json.dumps([p.get("stats") for p in before], ensure_ascii=False))

        # ── 4. 用例 ① set_starred 真写 + 全 chunk 一致 ────────────
        r1 = qb.set_starred("D1", True)
        print("  set_starred(D1,True) 返回:", json.dumps(r1, ensure_ascii=False))
        check("① set_starred(D1,True) ok=True", r1["ok"] is True, f"updated={r1['updated']}")
        check("① updated == D1 chunk 数(2)", r1["updated"] == 2, f"updated={r1['updated']}")
        after = [p for p in qb.scroll_payloads() if p["doc_id"] == "D1"]
        print("  写后 D1 stats 原文:", json.dumps([p.get("stats") for p in after], ensure_ascii=False))
        check("① 全 chunk starred 一致（真实值）",
              len(after) == 2 and all(p["stats"].get("starred") is True for p in after),
              f"starred列表={[p['stats'].get('starred') for p in after]}")

        # ── 5. 用例 ② access_count 保留 ───────────────────────────
        b_stats = [p.get("stats") for p in before]
        a_stats = [p.get("stats") for p in after]
        check("② access_count 未丢（stats 原文对比）",
              [s.get("access_count") for s in b_stats] == [s.get("access_count") for s in a_stats],
              f"before={b_stats}  after={a_stats}")

        # ── 6. 用例 ③ 幂等重复写 ─────────────────────────────────
        r2 = qb.set_starred("D1", True)
        print("  set_starred(D1,True) 第二次 返回:", json.dumps(r2, ensure_ascii=False))
        check("③ 幂等重复写 ok=True", r2["ok"] is True, f"updated={r2['updated']}")
        after2 = [p for p in qb.scroll_payloads() if p["doc_id"] == "D1"]
        check("③ 重复写后仍全 starred（真实值）",
              all(p["stats"].get("starred") is True for p in after2),
              f"starred列表={[p['stats'].get('starred') for p in after2]}")

        # ── 7. 用例 ④ 不存在 doc_id ──────────────────────────────
        r3 = qb.set_starred("NOEXIST_DOC", True)
        print("  set_starred(NOEXIST_DOC,True) 返回:", json.dumps(r3, ensure_ascii=False))
        check("④ 不存在 doc_id → ok=False", r3["ok"] is False, f"error={r3.get('error')}")
        check("④ 不存在 doc_id → updated=0", r3["updated"] == 0, f"updated={r3['updated']}")

        # ── 8. 用例 ⑤ 跨周收藏被 fetch_dashboard_docs 捞到 ───────
        data = qb.fetch_dashboard_docs()
        week_ids = [d["doc_id"] for d in data["week"]]
        starred_ids = [d["doc_id"] for d in data["starred"]]
        print("  fetch_dashboard_docs → week:", week_ids, "| starred:", starred_ids)
        check("⑤ 本周区含 D2 不含 D1", "D2" in week_ids and "D1" not in week_ids,
              f"week={week_ids}")
        check("⑤ 跨周收藏 D1 被 starred 捞到", "D1" in starred_ids and "D2" not in starred_ids,
              f"starred={starred_ids}")
        check("⑤ fetch_starred_docs 与 starred 一致", [d["doc_id"] for d in qb.fetch_starred_docs()] == starred_ids,
              f"fetch_starred_docs={[d['doc_id'] for d in qb.fetch_starred_docs()]}")
        # 瞬态标记在内存中正确
        d1_mem = next(d for d in data["starred"] if d["doc_id"] == "D1")
        d2_mem = next(d for d in data["week"] if d["doc_id"] == "D2")
        check("⑤ 瞬态标记 _starred/_this_week 内存值正确",
              d1_mem.get("_starred") is True and d1_mem.get("_this_week") is False
              and d2_mem.get("_starred") is False and d2_mem.get("_this_week") is True,
              f"D1(_starred={d1_mem.get('_starred')},_this_week={d1_mem.get('_this_week')}) "
              f"D2(_starred={d2_mem.get('_starred')},_this_week={d2_mem.get('_this_week')})")

        # ── 9. 用例 ⑥ 瞬态标记严禁回写 Qdrant ────────────────────
        raw_after = rest("POST", f"collections/{TMP}/points/scroll",
                         {"with_payload": True, "with_vector": False, "limit": 10})
        raw_payloads = [p.get("payload") or {} for p in (raw_after.get("result") or {}).get("points") or []]
        leaked = [k for p in raw_payloads for k in p if k.startswith("_")]
        check("⑥ Qdrant 原始 payload 无下划线瞬态键", not leaked,
              f"原始 payload keys 样例={list(raw_payloads[0].keys()) if raw_payloads else '空'}")

        # ── 10. 用例 ⑦a is_starred 三层容错（纯函数，不碰 Qdrant）──
        check("⑦ is_starred({}) → False（stats 缺失）", qb.is_starred({}) is False)
        check("⑦ is_starred(stats 非 dict) → False", qb.is_starred({"stats": "oops"}) is False)
        check("⑦ is_starred(stats 无 starred) → False",
              qb.is_starred({"stats": {"access_count": 1}}) is False)
        check("⑦ is_starred(starred=False) → False",
              qb.is_starred({"stats": {"access_count": 1, "starred": False}}) is False)
        check("⑦ is_starred(starred=True) → True",
              qb.is_starred({"stats": {"access_count": 1, "starred": True}}) is True)

        # ── 11. 用例 ⑦b 空集合 fetch_dashboard_docs 不崩 ─────────
        qb.QDRANT_COLLECTION = TMP_EMPTY
        empty_data = qb.fetch_dashboard_docs()
        check("⑦ 空集合 → week=[] 且 starred=[] 不崩",
              empty_data["week"] == [] and empty_data["starred"] == [],
              f"week={empty_data['week']} starred={empty_data['starred']}")
        qb.QDRANT_COLLECTION = TMP

        # ── 12. 用例 ⑦c Qdrant 离线/写阶段异常 → ok=False 不抛 ───
        orig_post = qb._post
        def flaky_post(path: str, body: dict, timeout: int = 8) -> dict:
            if "payload" in path:
                raise urllib.error.URLError("simulated qdrant offline")
            return orig_post(path, body, timeout)
        qb._post = flaky_post
        try:
            r_off = qb.set_starred("D1", False)
            print("  set_starred(D1,False) 模拟写阶段异常 返回:", json.dumps(r_off, ensure_ascii=False))
            check("⑦ 写阶段异常 → ok=False 不抛", r_off["ok"] is False and r_off["error"] is not None,
                  f"error={r_off.get('error')}")
        finally:
            qb._post = orig_post

        # ── 13. 还原 D1=False（自验不留痕）────────────────────────
        r4 = qb.set_starred("D1", False)
        check("还原 D1=False ok", r4["ok"] is True, f"updated={r4['updated']}")

        # ── 14. 生产集合零污染验证 ────────────────────────────────
        prod_after = snapshot_prod()
        check("⑧ 生产集合 doc_id 集合不变",
              set(prod_after.keys()) == set(prod_before.keys()),
              f"before={len(prod_before)} after={len(prod_after)}")
        same_stats = prod_before == prod_after
        if not same_stats:
            diff = {k: (prod_before.get(k), prod_after.get(k))
                    for k in set(prod_before) | set(prod_after)
                    if prod_before.get(k) != prod_after.get(k)}
            check("⑧ 生产集合 stats 原文不变", False, f"差异={json.dumps(diff, ensure_ascii=False)[:500]}")
        else:
            check("⑧ 生产集合 stats 原文不变", True, "全部 doc stats 快照一致")

    finally:
        # ── 清理临时集合 ─────────────────────────────────────────
        for c in (TMP, TMP_EMPTY):
            try:
                deleted = rest("DELETE", f"collections/{c}")
                print(f"🧹 清理临时集合 {c} DELETE →", deleted.get("result"))
            except Exception as e:  # noqa: BLE001
                print(f"⚠️ 清理临时集合 {c} 失败（可手工删除）：{e}")

    print()
    if FAILURES:
        print(f"❌ T03 QA 验收未通过：{len(FAILURES)} 项失败 → {FAILURES}")
        return 1
    print("✅ T03 QA 验收全部通过（生产集合 athanor_v1 未被触碰）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
