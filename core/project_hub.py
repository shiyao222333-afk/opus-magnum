"""
OpusMagnum · 巨作 / GreatWork — 项目连接器客户端
封装对各子项目 API 的调用（按 api_spec.md 规范）。
"""

import requests
from typing import Optional, Any
from config.settings import settings, ProjectConfig


def _headers() -> dict:
    """构造带 API Key 的请求头。"""
    return {
        "Content-Type": "application/json",
        "X-Api-Key": settings.api_key,
    }


# ─── Citrinitas 客户端 ────────────────────────────────────────────────

def athanor_ingest_document(doc: dict) -> dict:
    """
    推送文档到 Citrinitas 知识库。
    调用：POST http://localhost:8080/api/documents/ingest
    """
    url = settings.athanor.endpoint("/api/documents/ingest")
    try:
        resp = requests.post(url, json=doc, headers=_headers(), timeout=10)
        return resp.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def athanor_search(query: str, kb_name: str = "default", limit: int = 5) -> list:
    """
    在 Citrinitas 知识库搜索。
    调用：GET http://localhost:8080/api/documents/search?q=...
    """
    url = settings.athanor.endpoint("/api/documents/search")
    params = {"q": query, "kb_name": kb_name, "limit": limit}
    try:
        resp = requests.get(url, params=params, headers=_headers(), timeout=10)
        data = resp.json()
        return data.get("results", [])
    except Exception:
        return []


# ─── 通用：获取项目状态摘要 ─────────────────────────────────────────

def get_project_summary(project: ProjectConfig) -> dict:
    """
    通用方法：检测任意项目的健康状态，返回状态摘要。
    用于仪表盘展示。复用 health_check（含 TCP 端口兜底，
    兼容 Streamlit / NiceGUI 等不提供 /health 端点的框架）。
    """
    from core.health_check import check_health
    return check_health(project)
