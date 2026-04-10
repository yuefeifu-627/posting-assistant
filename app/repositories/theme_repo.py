"""主题 Repository"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Theme, Post


class ThemeRepository:
    """主题数据访问"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Theme]:
        """根据ID获取主题"""
        return self.db.query(Theme).filter(Theme.id == id).first()

    def get_by_name(self, name: str) -> Optional[Theme]:
        """根据名称获取主题"""
        return self.db.query(Theme).filter(Theme.name == name).first()

    def get_all(self, skip: int = 0, limit: int = 20) -> List[Theme]:
        """获取主题列表"""
        return self.db.query(Theme).order_by(Theme.created_at.desc()).offset(skip).limit(limit).all()

    def count(self) -> int:
        """获取主题总数"""
        return self.db.query(Theme).count()

    def get_post_count(self, theme_id: int) -> int:
        """获取主题下的帖子数量"""
        return self.db.query(func.count(Post.id)).filter(Post.theme_id == theme_id).scalar() or 0

    def create(self, name: str, post_length: int = 500) -> Theme:
        """创建主题"""
        theme = Theme(name=name, post_length=post_length)
        self.db.add(theme)
        self.db.commit()
        self.db.refresh(theme)
        return theme

    def update(self, theme: Theme, name: str = None, post_length: int = None) -> Theme:
        """更新主题"""
        if name is not None:
            theme.name = name
        if post_length is not None:
            theme.post_length = post_length
        self.db.commit()
        self.db.refresh(theme)
        return theme

    def delete(self, theme: Theme) -> None:
        """删除主题"""
        self.db.delete(theme)
        self.db.commit()