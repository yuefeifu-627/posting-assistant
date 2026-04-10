"""依赖注入容器模块"""

from app.di.container import DIContainer, get_container, reset_container
from app.di.interfaces import (
    IThemeRepository,
    IPostRepository,
    ICorpusRepository,
    IThemeService,
    IPostService,
    ICorpusService,
    IAIService,
)

__all__ = [
    "DIContainer",
    "get_container",
    "reset_container",
    "IThemeRepository",
    "IPostRepository",
    "ICorpusRepository",
    "IThemeService",
    "IPostService",
    "ICorpusService",
    "IAIService",
]
