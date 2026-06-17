"""
📋 开发进度 — OpusMagnum
从 GitHub Issues 读取所有项目的任务，集中展示和管理。
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="开发进度 - OpusMagnum", page_icon="📋", layout="wide")

from utils.ui_utils import load_global_css, render_sidebar
load_global_css()
render_sidebar()

st.title("📋 开发进度")
st.caption("从 GitHub Issues 自动同步 — 集中查看所有项目的任务")

# ── 筛选栏 ──────────────────────────────────────
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    state_filter = st.selectbox("状态", ["open", "closed", "all"])
with col2:
    project_filter = st.multiselect(
        "项目",
        ["athanor", "alembic", "crucible", "opus-magnum"],
        default=["athanor", "alembic", "crucible", "opus-magnum"],
    )
with col3:
    if st.button("🔄 刷新", use_container_width=True):
        st.rerun()

st.divider()

# ── 读取数据 ──────────────────────────────────────
from core.dashboard import get_all_tasks

tasks = get_all_tasks(state=state_filter)

# 按项目筛选
if project_filter:
    tasks = [t for t in tasks if t.get("project_label", "") in project_filter]

# ── 展示 ──────────────────────────────────────────
if not tasks:
    st.info("暂无任务数据。\n\n💡 去各项目仓库建 Issue，这里会自动同步。")
    st.markdown("### 快速建 Issue：")
    cols = st.columns(4)
    urls = [
        "https://github.com/shiyao222333-afk/athanor/issues/new",
        "https://github.com/shiyao222333-afk/alembic/issues/new",
        "https://github.com/shiyao222333-afk/crucible/issues/new",
        "https://github.com/shiyao222333-afk/opus-magnum/issues/new",
    ]
    labels = ["🏭 Athanor", "⚗️ Alembic", "🔬 Crucible", "⚛️ OpusMagnum"]
    for col, url, label in zip(cols, urls, labels):
        with col:
            st.markdown(f"[➕ {label}]({url})")

else:
    # 统计卡片
    total = len(tasks)
    open_count = sum(1 for t in tasks if t.get("status") != "done")
    done_count = total - open_count

    stat_cols = st.columns(3)
    with stat_cols[0]:
        st.metric("总任务", total)
    with stat_cols[1]:
        st.metric("进行中", open_count)
    with stat_cols[2]:
        st.metric("已完成", done_count)

    st.divider()

    # 按项目分组展示
    df = pd.DataFrame([
        {
            "项目": t.get("project_label", ""),
            "标题": t.get("title", ""),
            "状态": "✅" if t.get("status") == "done" else "📋",
            "标签": ", ".join(t.get("labels", [])),
            "更新": t.get("updated_at", "")[:10],
            "链接": t.get("github_issue_url", ""),
        }
        for t in tasks
    ])

    # 点击标题跳转到 GitHub Issue
    for _, row in df.iterrows():
        col_title, col_status, col_labels, col_updated = st.columns([4, 1, 2, 1])
        with col_title:
            st.markdown(f"[{row['标题']}]({row['链接']})")
        with col_status:
            st.write(row["状态"])
        with col_labels:
            st.caption(row["标签"])
        with col_updated:
            st.caption(row["更新"])

st.divider()
st.caption(f"最后同步：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
