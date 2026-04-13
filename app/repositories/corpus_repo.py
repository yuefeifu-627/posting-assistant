"""语料库 Repository"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import UserPost, StyleProfile


class CorpusRepository:
    """语料库数据访问"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_post_by_id(self, id: int) -> Optional[UserPost]:
        """根据ID获取用户帖子"""
        return self.db.query(UserPost).filter(UserPost.id == id).first()

    def get_all_user_posts(self, tag: str = None, skip: int = 0, limit: int = 20) -> List[UserPost]:
        """获取用户帖子列表"""
        query = self.db.query(UserPost)
        if tag:
            query = query.filter(UserPost.tags.contains(tag))
        return query.order_by(UserPost.created_at.desc()).offset(skip).limit(limit).all()

    def count_user_posts(self, tag: str = None) -> int:
        """获取用户帖子总数"""
        query = self.db.query(UserPost)
        if tag:
            query = query.filter(UserPost.tags.contains(tag))
        return query.count()

    def get_all_user_posts_content(self) -> List[str]:
        """获取所有用户帖子的内容"""
        posts = self.db.query(UserPost).all()
        return [p.content for p in posts]

    def create_user_post(self, content: str, title: str = None, tags: str = None, note: str = None) -> UserPost:
        """创建用户帖子"""
        post = UserPost(
            title=title,
            content=content,
            tags=tags,
            note=note
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update_user_post(self, post: UserPost, title: str = None, content: str = None, tags: str = None, note: str = None) -> UserPost:
        """更新用户帖子"""
        if title is not None:
            post.title = title
        if content is not None:
            post.content = content
        if tags is not None:
            post.tags = tags
        if note is not None:
            post.note = note
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete_user_post(self, post: UserPost) -> None:
        """删除用户帖子"""
        self.db.delete(post)
        self.db.commit()

    def get_style_profile(self) -> Optional[StyleProfile]:
        """获取风格特征"""
        return self.db.query(StyleProfile).first()

    def create_or_update_style_profile(self, content: str, post_count: int) -> StyleProfile:
        """创建或更新风格特征"""
        profile = self.get_style_profile()
        if profile:
            profile.content = content
            profile.post_count = post_count
        else:
            profile = StyleProfile(content=content, post_count=post_count)
            self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile