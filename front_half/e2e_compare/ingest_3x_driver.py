"""
熔知摄入 3 次一致性测试驱动。
复刻 watcher 流程：classify_document -> ingest(metadata=...)，同一文档跑 3 次，
每次强制重录到独立测试集合，读回 payload 字段 + 向量，对比各字段是否出现差异。
"""
import json
import os
import sys
import requests

# 必须在 Citrinitas 目录下运行（绝对 import：classify_pipeline / services / text_pipeline ...）
CIT_DIR = "D:/citrinitas"
os.chdir(CIT_DIR)
sys.path.insert(0, CIT_DIR)

from classify_pipeline import classify_document
from services.ingest_service import ingest
from text_pipeline import parse_frontmatter

QDRANT_URL = "http://127.0.0.1:6333"
COL = "athanor_3x_test"
FILE_PATH = "D:/opus-magnum/front_half/e2e_compare/run1/nigredo_transit.md"

# 重点比对的 payload 字段
FACET_FIELDS = [
    "content_type", "domain", "temporal_nature", "epistemic_status",
    "trust_score", "knowledge_type", "is_personal", "language",
    "project_source", "lifecycle", "author", "udc_code", "needs_review",
]
FREE_FIELDS = ["title", "keywords", "auto_summary"]


def read_text(fp):
    with open(fp, "r", encoding="utf-8") as f:
        return f.read()


def scroll_payloads(doc_id):
    """读回该 doc_id 在测试集合中的全部 point（payload + vector）。"""
    out = []
    next_off = None
    while True:
        body = {
            "filter": {"must": [{"key": "doc_id", "match": {"value": doc_id}}]},
            "with_payload": True,
            "with_vector": True,
            "limit": 100,
        }
        if next_off:
            body["offset"] = next_off
        r = requests.post(f"{QDRANT_URL}/collections/{COL}/points/scroll",
                          json=body, timeout=15)
        j = r.json().get("result", {})
        out.extend(j.get("points", []))
        next_off = j.get("next_page_offset")
        if next_off is None:
            break
    return out


def _as_dense(v):
    """具名向量(dict)取 dense；已是 list 则原样返回。"""
    if isinstance(v, dict):
        if "dense" in v:
            return v["dense"]
        # 退回取第一个 list 值
        for val in v.values():
            if isinstance(val, list):
                return val
        return None
    return v


def cosine(a, b):
    a, b = _as_dense(a), _as_dense(b)
    if not a or not b or len(a) != len(b):
        return None
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return None
    return dot / (na * nb)


def main():
    raw = read_text(FILE_PATH)
    # 测试"单一入口"行为：直接传【含 frontmatter 的原文】给 classify_document，
    # 不预先解析、不显式传 title/author —— 由 classify_document 内部解析（同 dlq 死信路径）。
    # 这是最强的验证：若连"不预解析"的调用方都能拿到稳定标题，则 watcher/网页上传（也传 fm）必无问题。
    clean_text, fm = parse_frontmatter(raw)
    runs = []
    for run in range(3):
        # 1) 分类（仅传 source_path，标题/作者由 classify_document 从 frontmatter 提取）
        file_metadata = {"source_path": FILE_PATH}
        cls = classify_document(raw, file_metadata=file_metadata)
        classification = cls.get("classification", {})
        annotated = cls.get("annotated", {})
        field_sources = annotated.get("field_sources", {})
        overall_conf = annotated.get("overall_confidence", 0.0)

        metadata = dict(classification)
        metadata["source_path"] = FILE_PATH
        metadata["ingestion_source"] = "watch"

        # 2) 摄入（force_reingest 绕过内容去重；用剥除 frontmatter 的干净正文，同 watcher 入库行为）
        res = ingest(
            text=clean_text,
            metadata=metadata,
            collection=COL,
            field_sources=field_sources,
            overall_confidence=overall_conf,
            file_path=FILE_PATH,
            force_reingest=True,
        )
        if not res.get("ok"):
            print(f"[RUN{run}] 摄入失败: {res.get('error')}")
            runs.append({"run": run, "ingest_ok": False, "error": res.get("error")})
            continue

        # 3) 读回 payload
        pts = scroll_payloads(res["doc_id"])
        payloads = [p.get("payload", {}) for p in pts]
        vectors = [p.get("vector") for p in pts if p.get("vector")]

        # 取第一个 chunk 的 payload 作代表，比对字段
        rep = payloads[0] if payloads else {}
        entry = {
            "run": run,
            "ingest_ok": True,
            "doc_id": res["doc_id"],
            "n_points": len(pts),
            "classification": classification,
            "payload": {k: rep.get(k) for k in FACET_FIELDS + FREE_FIELDS},
            "vectors": vectors,
        }
        runs.append(entry)
        print(f"[RUN{run}] ok | points={len(pts)} | doc_id={res['doc_id']}")

    # ── 比对 ──
    print("\n" + "=" * 70)
    print("字段差异比对（RUN0 vs RUN1 vs RUN2）")
    print("=" * 70)

    # 分类层字段
    print("\n── classify_document 层 ──")
    for f in FACET_FIELDS + FREE_FIELDS:
        vals = [r.get("classification", {}).get(f) for r in runs if r.get("ingest_ok")]
        if len(set(map(str, vals))) == 1:
            print(f"  [稳定] {f} = {vals[0]}")
        else:
            print(f"  [漂移] {f}:")
            for r, v in zip(runs, vals):
                if r.get("ingest_ok"):
                    print(f"         RUN{r['run']}: {v}")

    # 入库 payload 层字段（归一化后写入 Qdrant 的值）
    print("\n── 入库 payload 层（归一化后）──")
    for f in FACET_FIELDS + FREE_FIELDS:
        vals = [r.get("payload", {}).get(f) for r in runs if r.get("ingest_ok")]
        if len(set(map(str, vals))) == 1:
            print(f"  [稳定] {f} = {vals[0]}")
        else:
            print(f"  [漂移] {f}:")
            for r, v in zip(runs, vals):
                if r.get("ingest_ok"):
                    print(f"         RUN{r['run']}: {v}")

    # 向量一致性
    print("\n── 向量（嵌入）一致性 ──")
    vecs = [r["vectors"] for r in runs if r.get("ingest_ok") and r.get("vectors")]
    if len(vecs) >= 2:
        n0 = len(vecs[0])
        same_len = all(len(v) == n0 for v in vecs)
        print(f"  各 run 向量块数: {[len(v) for v in vecs]} (一致={same_len})")
        # 比较第一段向量余弦
        sims = []
        for i in range(1, len(vecs)):
            sim = cosine(vecs[0][0], vecs[i][0])
            sims.append((i, sim))
        for i, sim in sims:
            print(f"  RUN0 第一段 vs RUN{i} 第一段 cosine = {sim:.8f}")
    else:
        print("  向量数据不足，无法比对")

    # 落盘一份 JSON 供后续查看
    out_path = "D:/opus-magnum/front_half/e2e_compare/ingest_3x_result.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(runs, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n结果已写入: {out_path}")


if __name__ == "__main__":
    main()
