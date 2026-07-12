"""
🔗 项目连接器 — OpusMagnum
测试各项目 API 连通性，手动触发跨项目联动。
"""

import streamlit as st
import requests as req
from datetime import datetime

st.set_page_config(page_title="项目连接器 - OpusMagnum", page_icon="🔗", layout="wide")

from utils.ui_utils import load_global_css, render_sidebar
load_global_css()
render_sidebar()

st.title("🔗 项目连接器")
st.caption("测试各项目 API 连通性，手动触发跨项目联动")

# ── 读取配置 ──────────────────────────────────────
from config.settings import settings

st.divider()

# ── 区块 1：健康检查 ──────────────────────────────
st.subheader("📡 健康检查")
st.caption("检测各项目是否在线（HTTP /health 优先，端口监听兜底）")

cols = st.columns(4)
projects = [
    ("🏭 Citrinitas", settings.citrinitas),
    ("⚗️ Nigredo", settings.nigredo),
    ("🔬 Albedo", settings.albedo),
    ("✨ Rubedo", settings.rubedo),
]

for (label, proj), col in zip(projects, cols):
    with col:
        if st.button(f"Ping {label}", use_container_width=True, key=f"ping_{proj.name}"):
            from core.health_check import check_health
            result = check_health(proj)
            if result["online"]:
                st.success(f"✅ 在线\n版本：{result.get('version', '?')}")
            else:
                st.error(f"❌ 离线\n{result.get('status', '')}")

st.divider()

# ── 区块 2：手动联动操作 ─────────────────────────
st.subheader("⚡ 手动联动操作")
st.caption("直接调用各项目 API，测试联动是否打通。")

# --- Athanor：搜索知识库 ---
with st.expander("🏭 Athanor — 搜索知识库", expanded=False):
    search_query = st.text_input("搜索关键词", key="search_q")
    search_kb = st.text_input("知识库名称", value="default", key="search_kb")
    if st.button("🔍 搜索", key="btn_search"):
        if search_query:
            try:
                url = settings.citrinitas.endpoint("/api/documents/search")
                resp = req.get(
                    url,
                    params={"q": search_query, "kb_name": search_kb, "limit": 5},
                    headers={"X-Api-Key": settings.api_key},
                    timeout=10,
                )
                results = resp.json().get("results", [])
                if results:
                    for r in results:
                        st.markdown(f"**{r['title']}** — 相关度 {r['score']:.2f}")
                        st.caption(r["snippet"])
                else:
                    st.info("无结果")
            except Exception as e:
                st.error(f"调用失败：{e}")
        else:
            st.warning("请输入搜索关键词")

# --- Alembic：提交视频处理任务 ---
with st.expander("⚗️ Alembic — 提交视频任务", expanded=False):
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
                data = resp.json()
                st.success(f"任务已提交！task_id：{data.get('task_id', '?')}")
            except Exception as e:
                st.error(f"调用失败：{e}")
        else:
            st.warning("请输入视频链接")

# --- Crucible：触发矛盾检测 ---
with st.expander("🔬 Crucible — 触发矛盾检测", expanded=False):
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

# ── 区块 3：API 规范速查 ─────────────────────────
st.subheader("📖 API 规范速查")
st.caption("各项目需实现的端点列表（详见 api_spec.md）")

spec_data = [
    {"项目": "Athanor",  "端点": "GET /health",           "用途": "健康检查"},
    {"项目": "Athanor",  "端点": "POST /api/documents/ingest", "用途": "入库文档"},
    {"项目": "Athanor",  "端点": "GET /api/documents/search",  "用途": "搜索知识库"},
    {"项目": "Alembic", "端点": "POST /api/videos/submit",   "用途": "提交视频任务"},
    {"项目": "Alembic", "端点": "GET /api/videos/{id}/status", "用途": "查询进度"},
    {"项目": "Crucible", "端点": "POST /api/scan",            "用途": "触发检测"},
    {"项目": "Crucible", "端点": "GET /api/reports/latest",   "用途": "获取最新报告"},
]
st.dataframe(spec_data, use_container_width=True, hide_index=True)

st.caption(f"OpusMagnum · 巨作 / GreatWork — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
