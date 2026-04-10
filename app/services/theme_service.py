"""主题 Service"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.theme_repo import ThemeRepository
from app.exceptions import ThemeNotFound, ThemeDuplicate
from app.logger import get_logger

logger = get_logger("theme_service")


class ThemeService:
    """主题业务逻辑"""

    def __init__(self, db: Session):
        self.repo = ThemeRepository(db)

    def get_by_id(self, id: int) -> dict:
        """获取单个主题"""
        theme = self.repo.get_by_id(id)
        if not theme:
            raise ThemeNotFound(id)

        logger.info(f"获取主题: {theme.name} (ID: {id})")
        return self._build_response(theme)

    def get_all(self, skip: int = 0, limit: int = 20) -> dict:
        """获取主题列表"""
        themes = self.repo.get_all(skip, limit)
        total = self.repo.count()

        logger.info(f"获取主题列表: {len(themes)}/{total}")

        return {
            "themes": [self._build_response(theme) for theme in themes],
            "total": total
        }

    def create(self, name: str, post_length: int = 500) -> dict:
        """创建主题"""
        # 检查重复
        existing = self.repo.get_by_name(name)
        if existing:
            raise ThemeDuplicate()

        theme = self.repo.create(name, post_length)
        logger.info(f"创建主题: {theme.name} (ID: {theme.id})")

        return self._build_response(theme)

    def update(self, id: int, name: str = None, post_length: int = None) -> dict:
        """更新主题"""
        theme = self.repo.get_by_id(id)
        if not theme:
            raise ThemeNotFound(id)

        # 检查名称重复
        if name and name != theme.name:
            existing = self.repo.get_by_name(name)
            if existing:
                raise ThemeDuplicate()

        theme = self.repo.update(theme, name, post_length)
        logger.info(f"更新主题: {theme.name} (ID: {id})")

        return self._build_response(theme)

    def delete(self, id: int) -> None:
        """删除主题"""
        theme = self.repo.get_by_id(id)
        if not theme:
            raise ThemeNotFound(id)

        logger.info(f"删除主题: {theme.name} (ID: {id})")
        self.repo.delete(theme)

    def _build_response(self, theme) -> dict:
        """构建响应数据"""
        return {
            "id": theme.id,
            "name": theme.name,
            "post_length": theme.post_length,
            "created_at": theme.created_at,
            "updated_at": theme.updated_at,
            "post_count": self.repo.get_post_count(theme.id)
        }