"""
🎛️ 总指挥部 — OpusMagnum 唯一子页面
合并原「总仪表盘 / 开发进度 / 项目连接器」的去重后内容：
服务健康、仓库状态、任务看板、手动联动、API 速查、开发路线。
所有健康 / 任务数据均来自 core 单一数据源，不在多处重复拉取。
命名统一为 settings 定义的两段式（炼金阶段 + 中文），修正旧页端口与 Issue 链接错误。
"""

import streamlit as st
import requests as req
from datetime import datetime

from config.settings import settings
from utils.ui_utils import load_global_css, render_sidebar

st.set_page_config(page_title="总指挥部 - OpusMagnum", page_icon="🎛️", layout="wide")
load_global_css()
render_sidebar()

st.title("🎛️ 总指挥部")
st.caption("一人公司总指挥部 — 健康监控 · 任务 · 跨器联动（统一控制台）")

# 刷新
if st.button("🔄 刷新", use_container_width=True):
    st.rerun()

st.divider()

# ─── 1. 服务健康状态（全站唯一健康展示）────────────
st.subheader("📡 服务健康状态")
from core.health_check import check_all

health_data = check_all()
cols = st.columns(len(health_data))
for h in health_data:
    with cols[health_data.index(h)]:
        if h["online"]:
            extra = f"{h.get('latency_ms', '?')}ms" if h.get("latency_ms") is not None else "端口监听"
            st.success(f"**{h['project']}**\n\n在线 — {extra}")
        else:
            st.error(f"**{h['project']}**\n\n离线 — {h.get('status', 'unknown')}")

st.divider()

# ─── 2. GitHub 仓库状态 ───────────────────────────
st.subheader("📊 GitHub 仓库状态")
from core.dashboard import get_all_repo_summaries

repo_summaries = get_all_repo_summaries()
REPO_ALIAS = {
    "Citrinitas": "🏭 熔知",
    "Nigredo": "⚗️ 馏析",
    "Albedo": "🔬 炼真",
    "Rubedo": "✨ 凝华",
    "OpusMagnum": "⚛️ 巨作",
}
repo_order = ["Citrinitas", "Nigredo", "Albedo", "Rubedo", "OpusMagnum"]
cols = st.columns(len(repo_order))
for label, col in zip(repo_order, cols):
    data = repo_summaries.get(label, {})
    with col:
        if "error" in data:
            st.info(f"**{REPO_ALIAS.get(label, label)}**\n\n⚠️ GitHub Token 未配置")
        else:
            st.metric(
                label=REPO_ALIAS.get(label, label),
                value=f"{data.get('open_issues', 0)} open issues",
                delta=f"⭐ {data.get('stars', 0)} | 🔃 {data.get('last_commit', '—')}",
            )

st.divider()

# ─── 3. 任务看板（GitHub Issues 超集，含筛选+统计）──
st.subheader("📋 任务看板（来自 GitHub Issues）")
from core.dashboard import get_all_tasks

# GitHub 客户端返回的 project_label 是英文功能别名（athanor/alembic/...），
# 这里统一映射成与上方一致的两段式显示名，消除旧「开发进度」页的命名混乱。
PROJECT_ALIAS = {
    "athanor": "🏭 Citrinitas · 熔知",
    "alembic": "⚗️ Nigredo · 馏析",
    "crucible": "🔬 Albedo · 炼真",
    "aludel": "✨ Rubedo · 凝华",
    "opus-magnum": "⚛️ OpusMagnum · 巨作",
}
alias_to_key = {v: k for k, v in PROJECT_ALIAS.items()}

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    state_filter = st.selectbox("状态", ["open", "closed", "all"])
with col2:
    proj_options = list(PROJECT_ALIAS.values())
    selected = st.multiselect("项目", proj_options, default=proj_options)
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.rerun()

sel_keys = {alias_to_key[s] for s in selected}
all_tasks = get_all_tasks(state=state_filter)
tasks = [t for t in all_tasks if t.get("project_label", "") in sel_keys]

if not tasks:
    st.info("暂无任务数据。\n\n💡 去各项目仓库建 Issue，这里会自动同步。")
    st.markdown("### 快速建 Issue：")
    quick = [
        ("🏭 Citrinitas · 熔知", settings.citrinitas_repo),
        ("⚗️ Nigredo · 馏析", settings.nigredo_repo),
        ("🔬 Albedo · 炼真", settings.albedo_repo),
        ("⚛️ OpusMagnum · 巨作", settings.opus_repo),
    ]
    qcols = st.columns(len(quick))
    for (lbl, repo), c in zip(quick, qcols):
        with c:
            st.markdown(f"[➕ {lbl}](https://github.com/{repo}/issues/new)")
else:
    total = len(tasks)
    open_count = sum(1 for t in tasks if t.get("status") != "done")
    done_count = total - open_count
    sc = st.columns(3)
    sc[0].metric("总任务", total)
    sc[1].metric("进行中", open_count)
    sc[2].metric("已完成", done_count)
    st.divider()
    for t in tasks:
        col_title, col_status, col_labels, col_updated = st.columns([4, 1, 2, 1])
        with col_title:
            url = t.get("github_issue_url", "")
            # 直接用 GitHub API 返回的真实 Issue 链接，避免旧页硬编码错仓库
            st.markdown(f"[{t.get('title', '')}]({url})" if url else t.get("title", ""))
        with col_status:
            st.write("✅" if t.get("status") == "done" else "📋")
        with col_labels:
            st.caption(", ".join(t.get("labels", [])))
        with col_updated:
            st.caption((t.get("updated_at", "") or "")[:10])

st.divider()

# ─── 4. 手动联动操作（仅原「项目连接器」有，保留）──
st.subheader("⚡ 手动联动操作")
st.caption("直接调用各器 API，测试联动是否打通。")

with st.expander("🏭 Citrinitas · 熔知 — 搜索知识库", expanded=False):
    st.caption("（熔知读取 API 尚未实现，暂由巨作直读共享 Qdrant）")
    search_query = st.text_input("搜索关键词", key="search_q")
    if st.button("🔍 搜索", key="btn_search"):
        if search_query:
            try:
                from core.qdrant_bridge import search_docs
                results = search_docs(search_query, limit=10)
                if results:
                    for r in results:
                        title = r.get("title") or "(无标题)"
                        prev = (r.get("content_preview") or "")[:80]
                        st.markdown(f"**{title}**")
                        if prev:
                            st.caption(prev)
                else:
                    st.info("无结果")
            except Exception as e:
                st.error(f"搜索失败：{e}")
        else:
            st.warning("请输入搜索关键词")

with st.expander("⚗️ Nigredo · 馏析 — 提交视频任务", expanded=False):
    video_url = st.text_input("视频链接（B站）", key="video_url")
    if st.button("🚀 提交任务", key="btn_submit_video"):
        if video_url:
            try:
                url = settings.nigredo.endpoint("/api/videos/submit")
                resp = req.post(
                    url,
                    json={"url": video_url, "priority": "normal"},
                    headers={"X-Api-Key": settings.api_key},
                    timeout=10,
                )
                st.success(f"任务已提交！task_id：{resp.json().get('task_id', '?')}")
            except Exception as e:
                st.error(f"调用失败：{e}")
        else:
            st.warning("请输入视频链接")

with st.expander("🔬 Albedo · 炼真 — 触发矛盾检测", expanded=False):
    scan_kb = st.text_input("目标知识库", value="default", key="scan_kb")
    if st.button("🔍 开始检测", key="btn_scan"):
        try:
            url = settings.albedo.endpoint("/api/scan")
            resp = req.post(
                url,
                json={"kb_name": scan_kb, "mode": "full"},
                headers={"X-Api-Key": settings.api_key},
                timeout=10,
            )
            st.info(f"检测已触发。report_id：{resp.json().get('report_id', '?')}")
        except Exception as e:
            st.error(f"调用失败：{e}")

st.divider()

# ─── 5. API 规范速查（全站唯一一份）──────────────
st.subheader("📖 API 规范速查")
st.caption("各器需实现的端点列表（详见 api_spec.md）")

spec_data = [
    {"项目": "🏭 Citrinitas · 熔知", "端点": "GET /health", "用途": "健康检查"},
    {"项目": "🏭 Citrinitas · 熔知", "端点": "POST /api/documents/ingest", "用途": "入库文档"},
    {"项目": "🏭 Citrinitas · 熔知", "端点": "GET /api/documents/search", "用途": "搜索（熔知 API 待实现，巨作暂直读 Qdrant）"},
    {"项目": "⚗️ Nigredo · 馏析", "端点": "POST /api/videos/submit", "用途": "提交视频任务"},
    {"项目": "⚗️ Nigredo · 馏析", "端点": "GET /api/videos/{id}/status", "用途": "查询进度"},
    {"项目": "🔬 Albedo · 炼真", "端点": "POST /api/scan", "用途": "触发检测"},
    {"项目": "🔬 Albedo · 炼真", "端点": "GET /api/reports/latest", "用途": "获取最新报告"},
]
st.dataframe(spec_data, use_container_width=True, hide_index=True)

st.divider()

# ─── 6. 开发路线 ───────────────────────────────────
st.subheader("🧭 开发路线")
st.markdown("""
| 阶段 | 项目 | 状态 |
|------|------|:--:|
| Phase 1 地基 | 🏭 Citrinitas · 熔知 | ✅ MVP |
| Phase 1 地基 | ⚗️ Nigredo · 馏析 | 📋 骨架 |
| Phase 1 地基 | 🔬 Albedo · 炼真 | 📋 骨架 |
| Phase 2 摄取 | Nigredo · 馏析 v0.1 | B站→字幕→文档 |
| Phase 3 验证 | Albedo · 炼真 v0.1 | 认知精炼（验真+提质） |
| Phase 4 输出 | ✨ Rubedo · 凝华 | 📋 v0.2.0 进行中 |
""")

st.divider()
st.caption(f"OpusMagnum · 巨作 / GreatWork — 最后刷新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
