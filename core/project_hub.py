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


# ─── Athanor 客户端 ────────────────────────────────────────────────

def athanor_ingest_document(doc: dict) -> dict:
    """
    推送文档到 Athanor 知识库。
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
    在 Athanor 知识库搜索。
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


# ─── Alembic 客户端 ────────────────────────────────────────────────

def alembic_submit_video(url: str, priority: str = "normal") -> dict:
    """
    提交视频处理任务到 Alembic。
    调用：POST http://localhost:8502/api/videos/submit
    """
    endpoint = settings.alembic.endpoint("/api/videos/submit")
    try:
        resp = requests.post(
            endpoint,
            json={"url": url, "priority": priority},
            headers=_headers(),
            timeout=10,
        )
        return resp.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def alembic_get_video_status(video_id: str) -> dict:
    """
    查询视频处理状态。
    调用：GET http://localhost:8502/api/videos/{video_id}/status
    """
    url = settings.alembic.endpoint(f"/api/videos/{video_id}/status")
    try:
        resp = requests.get(url, headers=_headers(), timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


# ─── Crucible 客户端 ────────────────────────────────────────────────

def crucible_trigger_scan(kb_name: str, mode: str = "full") -> dict:
    """
    触发 Crucible 矛盾检测。
    调用：POST http://localhost:8503/api/scan
    """
    url = settings.crucible.endpoint("/api/scan")
    try:
        resp = requests.post(
            url,
            json={"kb_name": kb_name, "mode": mode},
            headers=_headers(),
            timeout=10,
        )
        return resp.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def crucible_get_latest_report() -> dict:
    """
    获取 Crucible 最新矛盾报告摘要。
    调用：GET http://localhost:8503/api/reports/latest
    """
    url = settings.crucible.endpoint("/api/reports/latest")
    try:
        resp = requests.get(url, headers=_headers(), timeout=10)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


# ─── 通用：获取项目状态摘要 ─────────────────────────────────────────

def get_project_summary(project: ProjectConfig) -> dict:
    """
    通用方法：调用任意项目的 /health 端点，返回状态摘要。
    用于仪表盘展示。
    """
    try:
        resp = requests.get(project.endpoint("/health"), timeout=3)
        if resp.status_code == 200:
            return {"online": True, **resp.json()}
        return {"online": False, "status": f"http_{resp.status_code}"}
    except Exception:
        return {"online": False, "status": "offline"}
