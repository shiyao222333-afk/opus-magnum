"""
OpusMagnum · 巨作 / GreatWork — GitHub API 客户端
使用 requests 直接调 GitHub REST API（替代 LGPL 许可的 PyGithub），
仅保留本项目需要的读取能力：Issues 列表、跨项目 Issues、仓库摘要。
缺 token 或网络异常时优雅降级（返回空结果 / 错误字典），不抛异常。
"""

from typing import Optional, Union
import requests
from config.settings import settings

API_BASE = "https://api.github.com"
TIMEOUT = 15


class GitHubClient:
    """轻量 GitHub REST API 客户端。"""

    def __init__(self):
        self.token = settings.github_token

    def _headers(self) -> dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _get(self, url: str, params: Optional[dict] = None) -> Optional[Union[dict, list]]:
        """GET 请求；失败（无 token / 401 / 网络错误）返回 None。"""
        try:
            resp = requests.get(
                url, headers=self._headers(), params=params, timeout=TIMEOUT
            )
            if resp.status_code in (401, 403):
                return None
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException:
            return None

    def list_issues(self, repo_full_name: str, state: str = "open") -> list:
        """
        读取仓库 Issues（自动过滤 Pull Request）。
        返回格式符合 task.schema.json（简化版）。
        """
        if not repo_full_name:
            return []
        url = f"{API_BASE}/repos/{repo_full_name}/issues"
        data = self._get(url, params={"state": state, "per_page": 50})
        if not isinstance(data, list):
            return []
        issues = []
        for it in data[:50]:
            # GitHub 把 PR 也放进 issues 端点，这里跳过，只留真正的 Issue
            if "pull_request" in it:
                continue
            labels = [
                lb.get("name") for lb in it.get("labels", []) if isinstance(lb, dict)
            ]
            issues.append(
                {
                    "task_id": str(it.get("number")),
                    "title": it.get("title", ""),
                    "status": "done" if it.get("state") == "closed" else "todo",
                    "project": repo_full_name.split("/")[-1],
                    "labels": labels,
                    "github_issue_url": it.get("html_url", ""),
                    "created_at": it.get("created_at", "") or "",
                    "updated_at": it.get("updated_at", "") or "",
                }
            )
        return issues

    def list_all_issues(self, state: str = "open") -> dict:
        """读取所有子项目仓库的 Issues，按项目分组。"""
        repos = {
            "athanor": settings.citrinitas_repo,
            "alembic": settings.nigredo_repo,
            "crucible": settings.albedo_repo,
            "aludel": settings.rubedo_repo,
            "opus-magnum": settings.opus_repo,
        }
        result = {}
        for key, repo_name in repos.items():
            result[key] = self.list_issues(repo_name, state=state)
        return result

    def get_repo_summary(self, repo_full_name: str) -> dict:
        """
        获取仓库摘要：Issue 数量、最新提交、Stars。
        """
        if not repo_full_name:
            return {"error": "repo_not_found_or_token_missing"}
        data = self._get(f"{API_BASE}/repos/{repo_full_name}")
        if not isinstance(data, dict):
            return {"error": "repo_not_found_or_token_missing"}
        last_commit = "none"
        commits = self._get(
            f"{API_BASE}/repos/{repo_full_name}/commits", params={"per_page": 1}
        )
        if isinstance(commits, list) and commits:
            sha = commits[0].get("sha", "")
            last_commit = sha[:7] if sha else "none"
        return {
            "name": data.get("name", ""),
            "full_name": data.get("full_name", ""),
            "open_issues": data.get("open_issues_count", 0),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "default_branch": data.get("default_branch", ""),
            "last_commit": last_commit,
            "updated_at": data.get("updated_at", "") or "",
        }
