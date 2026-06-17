"""
OpusMagnum · 巨作 / GreatWork — UI 共享工具
侧边栏、全局 CSS、页面共用函数。
"""

import streamlit as st
from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent / "assets"


def load_global_css() -> None:
    """注入全局深色主题 CSS。"""
    css_file = ASSETS_DIR / "style.css"
    if css_file.exists():
        with open(css_file, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_sidebar() -> None:
    """渲染左侧导航栏。"""
    with st.sidebar:
        st.markdown("## ⚛️ OpusMagnum")
        st.markdown("##### 巨作 · GreatWork")
        st.divider()

        # 快速状态
        st.caption("快捷操作")
        if st.button("🔄 刷新所有状态", use_container_width=True):
            st.rerun()

        st.divider()

        # 外部链接
        st.markdown("🔗 [Athanor 知识库](http://localhost:8080)")
        st.markdown("🔗 [Alembic 视频提炼](http://localhost:8502)")
        st.markdown("🔗 [Crucible 矛盾检测](http://localhost:8503)")
        st.divider()

        st.caption("OpusMagnum · 一人公司总指挥部")
