"""服务接口定义 - 独立模块避免循环导入"""

from app.interfaces.service_interfaces import (
    IThemeRepository,
    IPostRepository,
    ICorpusRepository,
    IThemeService,
    IPostService,
    ICorpusService,
    IAIService,
)

__all__ = [
    "IThemeRepository",
    "IPostRepository",
    "ICorpusRepository",
    "IThemeService",
    "IPostService",
    "ICorpusService",
    "IAIService",
]
