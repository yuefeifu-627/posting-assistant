"""帖子 Service"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.post_repo import PostRepository
from app.repositories.theme_repo import ThemeRepository
from app.repositories.corpus_repo import CorpusRepository
from app.services.ai_service import AIService
from app.exceptions import PostNotFound, ThemeNotFound, AIServiceError
from app.logger import get_logger

logger = get_logger("post_service")


class PostService:
    """帖子业务逻辑"""

    def __init__(self, db: Session, ai_service: AIService):
        self.post_repo = PostRepository(db)
        self.theme_repo = ThemeRepository(db)
        self.corpus_repo = CorpusRepository(db)
        self.ai_service = ai_service

    def generate(self, theme_id: int, summary: str, requirements: str = None, post_length: int = None, use_api: bool = False) -> dict:
        """生成帖子"""
        # 获取主题
        theme = self.theme_repo.get_by_id(theme_id)
        if not theme:
            raise ThemeNotFound(theme_id)

        # 确定字数
        target_length = post_length if post_length else theme.post_length

        # 获取风格特征
        style_profile = None
        profile = self.corpus_repo.get_style_profile()
        if profile:
            style_profile = profile.content

        # AI 生成
        logger.info(f"生成帖子: 主题={theme.name}, 字数={target_length}, API={use_api}")
        try:
            content = self.ai_service.generate_post(
                theme=theme.name,
                summary=summary,
                requirements=requirements,
                post_length=target_length,
                use_api=use_api,
                style_profile=style_profile
            )
        except Exception as e:
            logger.error(f"AI生成失败: {str(e)}")
            raise AIServiceError(str(e))

        # 保存帖子
        post = self.post_repo.create(theme_id, content, summary, requirements)
        logger.info(f"帖子已保存: ID={post.id}")

        return self._build_response(post, theme.name)

    def create(self, theme_id: int, content: str, summary: str = None, requirements: str = None) -> dict:
        """手动创建帖子"""
        theme = self.theme_repo.get_by_id(theme_id)
        if not theme:
            raise ThemeNotFound(theme_id)

        post = self.post_repo.create(theme_id, content, summary, requirements)
        logger.info(f"手动创建帖子: ID={post.id}")

        return self._build_response(post, theme.name)

    def get_by_id(self, id: int) -> dict:
        """获取单个帖子"""
        post = self.post_repo.get_by_id(id)
        if not post:
            raise PostNotFound(id)

        theme = self.post_repo.get_theme(post.theme_id)
        return self._build_response(post, theme.name if theme else "")

    def get_all(self, theme_id: int = None, skip: int = 0, limit: int = 20) -> dict:
        """获取帖子列表"""
        posts = self.post_repo.get_all(theme_id, skip, limit)
        total = self.post_repo.count(theme_id)

        logger.info(f"获取帖子列表: {len(posts)}/{total}")

        result = []
        for post in posts:
            theme = self.post_repo.get_theme(post.theme_id)
            result.append(self._build_response(post, theme.name if theme else ""))

        return {"posts": result, "total": total}

    def update(self, id: int, content: str = None, summary: str = None, requirements: str = None) -> dict:
        """更新帖子"""
        post = self.post_repo.get_by_id(id)
        if not post:
            raise PostNotFound(id)

        post = self.post_repo.update(post, content, summary, requirements)
        logger.info(f"更新帖子: ID={id}")

        theme = self.post_repo.get_theme(post.theme_id)
        return self._build_response(post, theme.name if theme else "")

    def delete(self, id: int) -> None:
        """删除帖子"""
        post = self.post_repo.get_by_id(id)
        if not post:
            raise PostNotFound(id)

        logger.info(f"删除帖子: ID={id}")
        self.post_repo.delete(post)

    def _build_response(self, post, theme_name: str) -> dict:
        """构建响应数据"""
        return {
            "id": post.id,
            "theme_id": post.theme_id,
            "theme_name": theme_name,
            "summary": post.summary,
            "requirements": post.requirements,
            "content": post.content,
            "created_at": post.created_at,
            "updated_at": post.updated_at
        }