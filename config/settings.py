"""
OpusMagnum · 巨作 / GreatWork — 总指挥部配置
读取 .env，提供各项目地址、API Key 等全局配置。
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env（优先读项目根目录）
load_dotenv(Path(__file__).parent.parent / ".env")


def get_env(key: str, default: str = "") -> str:
    """读取环境变量，带默认值。"""
    return os.getenv(key, default)


class ProjectConfig:
    """单个子项目的连接配置。"""

    def __init__(self, name: str, port: int, url: str):
        self.name = name
        self.port = port
        self.url = url.rstrip("/")

    def endpoint(self, path: str) -> str:
        """拼接完整端点 URL。"""
        return f"{self.url}/{path.lstrip('/')}"


class Settings:
    """全局配置单例。"""

    def __init__(self):
        # API 认证
        self.api_key = get_env("OPUS_API_KEY", "opus-magnum-local")

        # OpusMagnum 自身
        self.opus_port = int(get_env("OPUSMAGNUM_PORT", "8500"))
        self.opus_url = get_env("OPUSMAGNUM_URL", "http://localhost:8500")

        # 各子项目
        self.citrinitas = ProjectConfig(
            name="Citrinitas · 熔知",
            port=int(get_env("ATHANOR_PORT", "8080")),
            url=get_env("ATHANOR_URL", "http://localhost:8080"),
        )
        self.nigredo = ProjectConfig(
            name="Nigredo · 馏析",
            port=int(get_env("ALEMBIC_PORT", "8502")),
            url=get_env("ALEMBIC_URL", "http://localhost:8502"),
        )
        self.albedo = ProjectConfig(
            name="Albedo · 炼真",
            port=int(get_env("CRUCIBLE_PORT", "8501")),
            url=get_env("CRUCIBLE_URL", "http://localhost:8501"),
        )
        self.rubedo = ProjectConfig(
            name="Rubedo · 凝华",
            port=int(get_env("ALUDEL_PORT", "8765")),
            url=get_env("ALUDEL_URL", "http://localhost:8765"),
        )

        # GitHub
        self.github_token = get_env("GITHUB_TOKEN", "")
        self.github_username = get_env("GITHUB_USERNAME", "shiyao222333-afk")
        self.citrinitas_repo = get_env("ATHANOR_REPO", "shiyao222333-afk/citrinitas")
        self.nigredo_repo = get_env("ALEMBIC_REPO", "shiyao222333-afk/nigredo")
        self.albedo_repo = get_env("CRUCIBLE_REPO", "shiyao222333-afk/albedo")
        self.rubedo_repo = get_env("ALUDEL_REPO", "shiyao222333-afk/rubedo")
        self.opus_repo = get_env("OPUSMAGNUM_REPO", "shiyao222333-afk/opus-magnum")

        # 日志
        self.log_level = get_env("LOG_LEVEL", "INFO").upper()

    @property
    def all_projects(self) -> list:
        """返回所有子项目配置列表。"""
        return [self.citrinitas, self.nigredo, self.albedo, self.rubedo]

    def get_project_by_name(self, name: str) -> ProjectConfig | None:
        """按名称查找项目配置。"""
        mapping = {
            "citrinitas": self.citrinitas,
            "nigredo": self.nigredo,
            "albedo": self.albedo,
            "rubedo": self.rubedo,
        }
        return mapping.get(name.lower())


# 全局单例
settings = Settings()
