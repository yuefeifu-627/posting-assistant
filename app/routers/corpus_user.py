"""支持用户系统的语料库路由"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.corpus_service_user import CorpusServiceUser
from app.services.ai_service import AIService
from app.di import IAIService
from app.dependencies import get_ai_service
from app.schemas import (
    UserPostCreate,
    UserPostUpdate,
    UserPostResponse,
    UserPostListResponse
)
from app.routers.auth import get_current_user
from app.models_user import User
from app.exceptions import AppException

router = APIRouter(prefix="/api/corpus", tags=["corpus"])


# === 风格分析相关 ===

@router.post("/analyze-style")
async def analyze_style(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_service: IAIService = Depends(get_ai_service)
):
    """分析当前用户的语料库，生成风格特征"""
    corpus_service = CorpusServiceUser(db, ai_service)
    result = corpus_service.analyze_writing_style(current_user.id)
    return result


@router.get("/style-profile")
async def get_style_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的风格特征"""
    corpus_service = CorpusServiceUser(db, None)
    return corpus_service.get_style_profile(current_user.id)


# === 语料库 CRUD ===

@router.post("/", response_model=UserPostResponse)
async def create_user_post(
    post_data: UserPostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加用户历史帖子到语料库"""
    corpus_service = CorpusServiceUser(db, None)
    result = corpus_service.create(
        content=post_data.content,
        title=post_data.title,
        tags=post_data.tags,
        note=post_data.note,
        user_id=current_user.id
    )
    return UserPostResponse(**result)


@router.get("/", response_model=UserPostListResponse)
async def list_user_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tag: Optional[str] = Query(None, description="按标签筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的语料库列表"""
    corpus_service = CorpusServiceUser(db, None)
    result = corpus_service.get_all(skip, limit, user_id=current_user.id, tag=tag)
    return UserPostListResponse(
        posts=[UserPostResponse(**p) for p in result["posts"]],
        total=result["total"]
    )


@router.get("/{post_id}", response_model=UserPostResponse)
async def get_user_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单篇用户帖子"""
    corpus_service = CorpusServiceUser(db, None)
    result = corpus_service.get_by_id(post_id, user_id=current_user.id)
    return UserPostResponse(**result)


@router.put("/{post_id}", response_model=UserPostResponse)
async def update_user_post(
    post_id: int,
    update_data: UserPostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户帖子"""
    corpus_service = CorpusServiceUser(db, None)
    result = corpus_service.update(
        post_id,
        title=update_data.title,
        content=update_data.content,
        tags=update_data.tags,
        note=update_data.note,
        user_id=current_user.id
    )
    return UserPostResponse(**result)


@router.delete("/{post_id}")
async def delete_user_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除用户帖子"""
    corpus_service = CorpusServiceUser(db, None)
    corpus_service.delete(post_id, user_id=current_user.id)
    return {"message": "帖子已删除"}