"""
🏠 总仪表盘 — OpusMagnum 首页
汇总所有子项目状态、任务、健康检测。
"""

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="总仪表盘 - OpusMagnum", page_icon="🏠", layout="wide")

# 加载全局 CSS + 侧边栏
from utils.ui_utils import load_global_css, render_sidebar
load_global_css()
render_sidebar()

st.title("🏠 总仪表盘")
st.caption("一人公司总指挥部 — 所有项目状态一览")

# ─── 刷新按钮 ────────────────────────────────────────
col_refresh = st.columns([1, 5])[0]
with col_refresh:
    if st.button("🔄 刷新", use_container_width=True):
        st.rerun()

st.divider()

# ─── 第一行：项目健康状态 ──────────────────────────
st.subheader("📡 服务健康状态")
from core.dashboard import get_health_df, get_health_summary

health_data = get_health_summary()
cols = st.columns(len(health_data))

for i, h in enumerate(health_data):
    with cols[i]:
        if h["online"]:
            st.success(f"**{h['project']}**\n\n在线 — {h.get('latency_ms', '?')}ms")
        else:
            st.error(f"**{h['project']}**\n\n离线 — {h.get('status', 'unknown')}")

st.divider()

# ─── 第二行：GitHub 仓库摘要 ──────────────────────
st.subheader("📊 GitHub 仓库状态")
from core.dashboard import get_all_repo_summaries

repo_summaries = get_all_repo_summaries()

col1, col2, col3, col4 = st.columns(4)
repos = [
    ("Athanor", repo_summaries.get("Athanor", {})),
    ("Alembic", repo_summaries.get("Alembic", {})),
    ("Crucible", repo_summaries.get("Crucible", {})),
    ("OpusMagnum", repo_summaries.get("OpusMagnum", {})),
]

for (label, data), col in zip(repos, [col1, col2, col3, col4]):
    with col:
        if "error" in data:
            st.info(f"**{label}**\n\n⚠️ GitHub Token 未配置")
        else:
            open_issues = data.get("open_issues", 0)
            stars = data.get("stars", 0)
            last_commit = data.get("last_commit", "—")
            st.metric(
                label=label,
                value=f"{open_issues} open issues",
                delta=f"⭐ {stars} | 🔃 {last_commit}",
            )

st.divider()

# ─── 第三行：近期任务（Issues）────────────────────
st.subheader("📋 近期任务（来自 GitHub Issues）")
from core.dashboard import get_tasks_df

tasks_df = get_tasks_df(state="open")

if tasks_df.empty:
    st.info("暂无 open 状态的 Issues。\n\n💡 去各项目仓库建 Issue 即可在此看到任务。")
else:
    # 按项目分组展示
    projects = tasks_df["项目"].unique()
    for proj in projects:
        st.markdown(f"**{proj}**")
        proj_df = tasks_df[tasks_df["项目"] == proj]
        st.dataframe(proj_df, use_container_width=True, hide_index=True)

st.divider()

# ─── 底部：快速操作 ────────────────────────────────
st.subheader("⚡ 快速操作")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown(
        "[➕ 打开 Athanor 建 Issue](https://github.com/shiyao222333-afk/athanor/issues/new)",
        unsafe_allow_html=False,
    )

with col_b:
    with st.expander("📖 API 规范速查"):
        st.markdown("""
| 项目 | 端点 | 用途 |
|------|------|------|
| Athanor | `GET /health` | 健康检查 |
| Athanor | `POST /api/documents/ingest` | 入库文档 |
| Athanor | `GET /api/documents/search` | 搜索知识库 |
| Alembic | `POST /api/videos/submit` | 提交视频任务 |
| Alembic | `GET /api/videos/{id}/status` | 查询进度 |
| Crucible | `POST /api/scan` | 触发检测 |
| Crucible | `GET /api/reports/latest` | 获取最新报告 |

认证方式：所有请求带 `X-Api-Key` 请求头。
        """)

with col_c:
    with st.expander("🧭 开发路线"):
        st.markdown("""
| 阶段 | 项目 | 状态 |
|------|------|:--:|
| Phase 1 地基 | 🏭 Athanor | ✅ MVP |
| Phase 1 地基 | ⚗️ Alembic | 📋 骨架 |
| Phase 1 地基 | 🔬 Crucible | 📋 骨架 |
| Phase 2 摄取 | Alembic v0.1 | B站→字幕→文档 |
| Phase 3 验证 | Crucible v0.1 | 矛盾检测 |
| Phase 4 输出 | Elixir | 远期 |
| Phase 5 自动化 | Homunculus | 远期 |
        """)

# ─── 页脚 ────────────────────────────────────────────
st.divider()
st.caption(f"OpusMagnum · 巨作 / GreatWork — 最后刷新：{datetime.now().strftime('%H:%M:%S')}")
