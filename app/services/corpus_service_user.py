"""支持用户系统的语料库 Service"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import UserPost, StyleProfile
from app.services.ai_service import AIService
from app.exceptions import UserPostNotFound, ValidationError, AIServiceError
from app.logger import get_logger

logger = get_logger("corpus_service_user")


class CorpusServiceUser:
    """支持用户系统的语料库业务逻辑"""

    def __init__(self, db: Session, ai_service: AIService):
        self.db = db
        self.ai_service = ai_service

    def create(self, content: str, title: str = None, tags: str = None, note: str = None, user_id: int = None) -> dict:
        """添加用户帖子到语料库"""
        if not content:
            raise ValidationError("帖子内容不能为空")

        # 创建用户帖子，如果提供了user_id则绑定到用户
        post_data = {
            "content": content,
            "title": title,
            "tags": tags,
            "note": note
        }

        if user_id:
            post_data["user_id"] = user_id

        post = UserPost(**post_data)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)

        logger.info(f"添加用户帖子: ID={post.id}, user_id={user_id}")
        return self._build_user_post_response(post)

    def get_by_id(self, id: int, user_id: int = None) -> dict:
        """获取单篇用户帖子"""
        query = self.db.query(UserPost).filter(UserPost.id == id)
        if user_id:
            # 如果指定了用户ID，确保只返回属于该用户的帖子
            query = query.filter(UserPost.user_id == user_id)

        post = query.first()
        if not post:
            raise UserPostNotFound(id)

        return self._build_user_post_response(post)

    def get_all(self, skip: int = 0, limit: int = 20, user_id: int = None, tag: str = None) -> dict:
        """获取用户帖子列表"""
        query = self.db.query(UserPost)

        # 只获取指定用户的帖子
        if user_id:
            query = query.filter(UserPost.user_id == user_id)

        # 按标签筛选
        if tag:
            query = query.filter(UserPost.tags.like(f"%{tag}%"))

        # 获取总数
        total = query.count()

        # 获取分页数据
        posts = query.order_by(UserPost.created_at.desc()).offset(skip).limit(limit).all()

        logger.info(f"获取语料库列表: {len(posts)}/{total}, user_id={user_id}")

        return {
            "posts": [self._build_user_post_response(p) for p in posts],
            "total": total
        }

    def update(self, id: int, title: str = None, content: str = None, tags: str = None, note: str = None, user_id: int = None) -> dict:
        """更新用户帖子"""
        query = self.db.query(UserPost).filter(UserPost.id == id)
        if user_id:
            query = query.filter(UserPost.user_id == user_id)

        post = query.first()
        if not post:
            raise UserPostNotFound(id)

        # 更新字段
        updates = {}
        if title is not None:
            updates["title"] = title
        if content is not None:
            updates["content"] = content
        if tags is not None:
            updates["tags"] = tags
        if note is not None:
            updates["note"] = note

        for key, value in updates.items():
            setattr(post, key, value)

        post.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(post)

        logger.info(f"更新用户帖子: ID={id}")
        return self._build_user_post_response(post)

    def delete(self, id: int, user_id: int = None) -> None:
        """删除用户帖子"""
        query = self.db.query(UserPost).filter(UserPost.id == id)
        if user_id:
            query = query.filter(UserPost.user_id == user_id)

        post = query.first()
        if not post:
            raise UserPostNotFound(id)

        self.db.delete(post)
        self.db.commit()
        logger.info(f"删除用户帖子: ID={id}")

    def analyze_writing_style(self, user_id: int) -> dict:
        """分析指定用户的写作风格"""
        # 只获取该用户的帖子
        posts = self.db.query(UserPost).filter(
            UserPost.user_id == user_id
        ).all()

        if len(posts) < 1:
            raise ValidationError("语料库中至少需要1篇帖子")

        # 提取所有内容
        contents = [post.content for post in posts]

        logger.info(f"开始分析用户 {user_id} 的写作风格: 共{len(contents)}篇帖子")

        try:
            style_profile = self.ai_service.analyze_writing_style(contents)
        except Exception as e:
            logger.error(f"风格分析失败: {str(e)}")
            raise AIServiceError(str(e))

        # 保存或更新风格特征
        profile = self.db.query(StyleProfile).filter(
            StyleProfile.user_id == user_id
        ).first()

        if profile:
            profile.content = style_profile
            profile.post_count = len(contents)
            profile.updated_at = datetime.utcnow()
        else:
            profile = StyleProfile(
                user_id=user_id,
                content=style_profile,
                post_count=len(contents)
            )
            self.db.add(profile)

        self.db.commit()
        logger.info(f"风格分析完成: 用户{user_id}基于{profile.post_count}篇帖子")

        return {
            "post_count": len(contents),
            "style_profile": style_profile
        }

    def get_style_profile(self, user_id: int) -> dict:
        """获取指定用户的风格特征"""
        profile = self.db.query(StyleProfile).filter(
            StyleProfile.user_id == user_id
        ).first()

        # 获取用户的语料库帖子数
        corpus_count = self.db.query(UserPost).filter(
            UserPost.user_id == user_id
        ).count()

        if not profile:
            return {
                "has_profile": False,
                "corpus_count": corpus_count,
                "profile": None
            }

        return {
            "has_profile": True,
            "corpus_count": corpus_count,
            "post_count": profile.post_count,
            "profile": profile.content,
            "updated_at": profile.updated_at
        }

    def _build_user_post_response(self, post) -> dict:
        """构建用户帖子响应"""
        return {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "tags": post.tags,
            "note": post.note,
            "created_at": post.created_at,
            "updated_at": post.updated_at
        }