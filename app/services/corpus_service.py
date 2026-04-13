"""语料库 Service"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.corpus_repo import CorpusRepository
from app.services.ai_service import AIService
from app.exceptions import UserPostNotFound, ValidationError, AIServiceError
from app.logger import get_logger

logger = get_logger("corpus_service")


class CorpusService:
    """语料库业务逻辑"""

    def __init__(self, db: Session, ai_service: AIService):
        self.repo = CorpusRepository(db)
        self.ai_service = ai_service

    def add_user_post(self, content: str, title: str = None, tags: str = None, note: str = None) -> dict:
        """添加用户帖子到语料库"""
        if not content:
            raise ValidationError("帖子内容不能为空")

        post = self.repo.create_user_post(content, title, tags, note)
        logger.info(f"添加用户帖子: ID={post.id}")

        return self._build_user_post_response(post)

    def get_user_post(self, id: int) -> dict:
        """获取单篇用户帖子"""
        post = self.repo.get_user_post_by_id(id)
        if not post:
            raise UserPostNotFound(id)

        return self._build_user_post_response(post)

    def get_all_user_posts(self, tag: str = None, skip: int = 0, limit: int = 20) -> dict:
        """获取用户帖子列表"""
        posts = self.repo.get_all_user_posts(tag, skip, limit)
        total = self.repo.count_user_posts(tag)

        logger.info(f"获取语料库列表: {len(posts)}/{total}")

        return {
            "posts": [self._build_user_post_response(p) for p in posts],
            "total": total
        }

    def update_user_post(self, id: int, title: str = None, content: str = None, tags: str = None, note: str = None) -> dict:
        """更新用户帖子"""
        post = self.repo.get_user_post_by_id(id)
        if not post:
            raise UserPostNotFound(id)

        post = self.repo.update_user_post(post, title, content, tags, note)
        logger.info(f"更新用户帖子: ID={id}")

        return self._build_user_post_response(post)

    def delete_user_post(self, id: int) -> None:
        """删除用户帖子"""
        post = self.repo.get_user_post_by_id(id)
        if not post:
            raise UserPostNotFound(id)

        logger.info(f"删除用户帖子: ID={id}")
        self.repo.delete_user_post(post)

    def analyze_style(self) -> dict:
        """分析写作风格"""
        contents = self.repo.get_all_user_posts_content()

        if len(contents) < 1:
            raise ValidationError("语料库中至少需要1篇帖子")

        logger.info(f"开始分析写作风格: 共{len(contents)}篇帖子")

        try:
            style_profile = self.ai_service.analyze_writing_style(contents)
        except Exception as e:
            logger.error(f"风格分析失败: {str(e)}")
            raise AIServiceError(str(e))

        # 保存风格特征
        profile = self.repo.create_or_update_style_profile(style_profile, len(contents))
        logger.info(f"风格分析完成: 基于{profile.post_count}篇帖子")

        return {
            "message": "风格分析完成",
            "post_count": len(contents),
            "style_profile": style_profile
        }

    def get_style_profile(self) -> dict:
        """获取风格特征"""
        profile = self.repo.get_style_profile()
        corpus_count = self.repo.count_user_posts()

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