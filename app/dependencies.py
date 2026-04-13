"""依赖注入定义 - 使用 DI 容器"""

from functools import lru_cache
from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.di import (
    DIContainer,
    IThemeService,
    IPostService,
    ICorpusService,
    get_container as di_get_container,
)
from app.di.interfaces import IAIService


def get_container() -> DIContainer:
    """获取 DI 容器单例"""
    return di_get_container()


def get_ai_service(
    container: DIContainer = Depends(get_container),
) -> IAIService:
    """获取 AI 服务（通过容器）"""
    return container.resolve(IAIService)


def get_theme_service(
    db: Session = Depends(get_db),
    container: DIContainer = Depends(get_container),
) -> IThemeService:
    """获取主题服务（通过容器）"""
    return container.resolve(IThemeService, db)


def get_post_service(
    db: Session = Depends(get_db),
    container: DIContainer = Depends(get_container),
) -> IPostService:
    """获取帖子服务（通过容器）"""
    return container.resolve(IPostService, db)


def get_corpus_service(
    db: Session = Depends(get_db),
    container: DIContainer = Depends(get_container),
) -> ICorpusService:
    """获取语料库服务（通过容器）"""
    return container.resolve(ICorpusService, db)
