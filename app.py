"""
OpusMagnum · 巨作 / GreatWork — 一人公司总指挥部（首页 = 📊 周看板）

阶段 2 知识消费侧：本周熔知新录入的一屏看板。
MVP 不依赖大模型，纯只读聚合（直读共享 Qdrant，见 core/qdrant_bridge.py）。
侧边栏自动列出 🎛️ 总指挥部 作为子页面。
"""

import sys
from pathlib import Path

# 将项目根目录加入 sys.path（让 core/ utils/ config/ 可直接 import）
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from datetime import datetime

from config.settings import settings
from utils.ui_utils import load_global_css, render_sidebar
from core.qdrant_bridge import fetch_week_docs, week_bounds, qdrant_reachable

st.set_page_config(
    page_title="OpusMagnum · 周看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_global_css()
render_sidebar()

st.title("📊 周看板")
monday, now = week_bounds()
st.caption(
    f"本周录入一览 · 周一 {monday.strftime('%Y-%m-%d')} ~ 今天 {now.strftime('%Y-%m-%d')}"
    f" ｜ 数据来自 🏭 熔知"
)

if st.button("🔄 刷新", use_container_width=False):
    st.rerun()


def _render_card(d: dict) -> None:
    """渲染单张知识卡（标题 + 主题标签 + 录入时间）。"""
    title = d.get("title") or "(无标题)"
    doms = d.get("domain") or []
    ca = d.get("created_at") or ""
    try:
        dt = datetime.fromisoformat(ca.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        tstr = dt.strftime("%m-%d %H:%M")
    except Exception:
        tstr = (ca or "—")[:16]
    with st.container(border=True):
        st.markdown(f"**{title}**")
        if doms:
            st.caption("🏷️ " + " · ".join(doms))
        st.caption(f"🕒 {tstr}")


# ── 连接探测：区分「知识库空」与「连不上」──
if not qdrant_reachable():
    st.error(
        "⚠️ 连不上熔知数据库（Qdrant）。\n\n"
        "请确认：① Qdrant 已启动（默认 127.0.0.1:6333）；"
        "② 已运行 start_all.bat 拉起整套系统。"
    )
    st.stop()

docs = fetch_week_docs()

if not docs:
    st.info(
        "📭 本周还没有新录入。\n\n"
        "去 🏭 熔知 添加知识后，这里会自动出现本周卡片。"
    )
    st.markdown(f"👉 [打开熔知知识库]({settings.citrinitas.url})")
    st.caption("OpusMagnum · 巨作 / GreatWork — 周看板（空态）")
    st.stop()

# ── 统计概览 ──
sources = {}
domains = set()
for d in docs:
    s = d.get("source") or "未知来源"
    sources[s] = sources.get(s, 0) + 1
    for dom in (d.get("domain") or []):
        domains.add(dom)

c1, c2, c3 = st.columns(3)
c1.metric("本周新增", f"{len(docs)} 条")
c2.metric("来源数", f"{len(sources)} 个")
c3.metric("主题数", f"{len(domains)} 个")

st.divider()
st.subheader("🗂️ 按来源分栏（看板）")
st.caption("同一来源的本周新录入归到同一栏，一屏纵览。")

# 按来源分组并保持时间降序
by_source: dict = {}
for d in docs:
    by_source.setdefault(d.get("source") or "未知来源", []).append(d)

src_list = list(by_source.keys())
per_row = min(len(src_list), 4)  # 一行最多 4 栏，超出换行
idx = 0
while idx < len(src_list):
    cols = st.columns(per_row)
    for ci in range(per_row):
        if idx >= len(src_list):
            break
        src = src_list[idx]
        items = by_source[src]
        with cols[ci]:
            st.markdown(f"**{src}** · {len(items)}")
            st.divider()
            for it in items:
                _render_card(it)
        idx += 1

st.divider()
st.caption("OpusMagnum · 巨作 / GreatWork — 周看板（只读聚合，MVP 不依赖大模型）")
