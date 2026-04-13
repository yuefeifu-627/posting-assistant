"""帖子 Repository"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Post, Theme


class PostRepository:
    """帖子数据访问"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Post]:
        """根据ID获取帖子"""
        return self.db.query(Post).filter(Post.id == id).first()

    def get_all(self, theme_id: int = None, skip: int = 0, limit: int = 20) -> List[Post]:
        """获取帖子列表"""
        query = self.db.query(Post)
        if theme_id:
            query = query.filter(Post.theme_id == theme_id)
        return query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

    def count(self, theme_id: int = None) -> int:
        """获取帖子总数"""
        query = self.db.query(Post)
        if theme_id:
            query = query.filter(Post.theme_id == theme_id)
        return query.count()

    def create(self, theme_id: int, content: str, summary: str = None, requirements: str = None) -> Post:
        """创建帖子"""
        post = Post(
            theme_id=theme_id,
            content=content,
            summary=summary,
            requirements=requirements
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update(self, post: Post, content: str = None, summary: str = None, requirements: str = None) -> Post:
        """更新帖子"""
        if content is not None:
            post.content = content
        if summary is not None:
            post.summary = summary
        if requirements is not None:
            post.requirements = requirements
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post: Post) -> None:
        """删除帖子"""
        self.db.delete(post)
        self.db.commit()

    def get_theme(self, theme_id: int) -> Optional[Theme]:
        """获取帖子所属主题"""
        return self.db.query(Theme).filter(Theme.id == theme_id).first()