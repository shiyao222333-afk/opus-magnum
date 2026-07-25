"""
OpusMagnum · 巨作 / GreatWork — 仪表盘数据聚合
汇总各项目状态、GitHub 数据、任务数据，供 UI 页面调用。
"""

import pandas as pd
from typing import Optional
from config.settings import settings
from core.health_check import check_all, format_health_badge
from core.github_client import GitHubClient


# 全局 GitHub 客户端（懒加载）
_gh_client: Optional[GitHubClient] = None


def _get_gh() -> GitHubClient:
    global _gh_client
    if _gh_client is None:
        _gh_client = GitHubClient()
    return _gh_client


# ─── 健康状态 ────────────────────────────────────────────────

def get_health_summary() -> list:
    """返回所有子项目的健康状态列表。"""
    return check_all()


def get_health_df() -> pd.DataFrame:
    """返回健康状态 DataFrame（供 Streamlit 表格展示）。"""
    data = check_all()
    return pd.DataFrame([
        {
            "项目": d.get("project", "unknown"),
            "状态": "✅ 在线" if d["online"] else "❌ 离线",
            "版本": d.get("version", "—"),
            "延迟(ms)": d.get("latency_ms", "—"),
        }
        for d in data
    ])


# ─── GitHub 仓库摘要 ─────────────────────────────────────────

def get_all_repo_summaries() -> dict:
    """获取所有子项目仓库摘要。"""
    gh = _get_gh()
    return {
        "Citrinitas": gh.get_repo_summary(settings.citrinitas_repo),
        "Nigredo": gh.get_repo_summary(settings.nigredo_repo),
        "Albedo": gh.get_repo_summary(settings.albedo_repo),
        "Rubedo": gh.get_repo_summary(settings.rubedo_repo),
        "OpusMagnum": gh.get_repo_summary(settings.opus_repo),
    }


# ─── 任务 / Issues ──────────────────────────────────────────

def get_all_tasks(state: str = "open") -> list:
    """
    获取所有项目的 Issues（作为任务）。
    返回扁平列表，带 project 字段。
    """
    gh = _get_gh()
    grouped = gh.list_all_issues(state=state)
    tasks = []
    for project_name, issues in grouped.items():
        for issue in issues:
            issue["project_label"] = project_name
            tasks.append(issue)
    return tasks


def get_tasks_df(state: str = "open") -> pd.DataFrame:
    """返回任务 DataFrame。"""
    tasks = get_all_tasks(state=state)
    if not tasks:
        return pd.DataFrame(columns=["项目", "标题", "状态", "标签", "更新时间"])
    return pd.DataFrame([
        {
            "项目": t.get("project_label", ""),
            "标题": t.get("title", ""),
            "状态": "✅ 已完成" if t.get("status") == "done" else "📋 " + t.get("status", ""),
            "标签": ", ".join(t.get("labels", [])),
            "更新时间": t.get("updated_at", "")[:10],
        }
        for t in tasks
    ])


# ─── 项目连接器状态（简易）────────────────────────────────

def get_project_api_status() -> pd.DataFrame:
    """
    检查各项目是否实现了 api_spec.md 定义的端点。
    目前只检查 /health，未来可扩展。
    """
    from core.project_hub import get_project_summary
    rows = []
    for project in settings.all_projects:
        summary = get_project_summary(project)
        rows.append({
            "项目": project.name,
            "/health": "✅" if summary.get("online") else "❌",
            "端口": project.port,
            "地址": project.url,
        })
    return pd.DataFrame(rows)
