"""语料库路由"""

from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.dependencies import get_corpus_service
from app.di import ICorpusService
from app.schemas import (
    UserPostCreate,
    UserPostUpdate,
    UserPostResponse,
    UserPostListResponse
)

router = APIRouter(prefix="/api/corpus", tags=["corpus"])


# === 风格分析相关（放在前面，避免被 /{post_id} 捕获）===

@router.post("/analyze-style")
async def analyze_style(
    service: ICorpusService = Depends(get_corpus_service),
):
    """分析语料库中的帖子，生成风格特征"""
    return service.analyze_writing_style()


@router.get("/style-profile")
async def get_style_profile(
    service: ICorpusService = Depends(get_corpus_service),
):
    """获取当前的风格特征"""
    return {"style_profile": service.get_style_profile()}


# === 语料库 CRUD ===

@router.post("/", response_model=UserPostResponse)
async def create_user_post(
    post_data: UserPostCreate,
    service: ICorpusService = Depends(get_corpus_service),
):
    """添加用户历史帖子到语料库"""
    result = service.create(
        content=post_data.content,
        title=post_data.title,
        tags=post_data.tags,
        note=post_data.note
    )
    return UserPostResponse(**result)


@router.get("/", response_model=UserPostListResponse)
async def list_user_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tag: Optional[str] = Query(None, description="按标签筛选"),
    service: ICorpusService = Depends(get_corpus_service),
):
    """获取用户语料库列表"""
    result = service.get_all(skip, limit)
    return UserPostListResponse(
        posts=[UserPostResponse(**p) for p in result["posts"]],
        total=result["total"]
    )


@router.get("/{post_id}", response_model=UserPostResponse)
async def get_user_post(
    post_id: int,
    service: ICorpusService = Depends(get_corpus_service),
):
    """获取单篇用户帖子"""
    result = service.get_by_id(post_id)
    return UserPostResponse(**result)


@router.put("/{post_id}", response_model=UserPostResponse)
async def update_user_post(
    post_id: int,
    update_data: UserPostUpdate,
    service: ICorpusService = Depends(get_corpus_service),
):
    """更新用户帖子"""
    result = service.update(
        post_id,
        title=update_data.title,
        content=update_data.content,
        tags=update_data.tags,
        note=update_data.note
    )
    return UserPostResponse(**result)


@router.delete("/{post_id}")
async def delete_user_post(
    post_id: int,
    service: ICorpusService = Depends(get_corpus_service),
):
    """删除用户帖子"""
    service.delete(post_id)
    return {"message": "帖子已删除"}
