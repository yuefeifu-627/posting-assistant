"""帖子路由"""

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_post_service
from app.di import IPostService
from app.schemas import (
    GeneratePostRequest,
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse
)

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("/generate", response_model=PostResponse)
async def generate_article(
    request: GeneratePostRequest,
    service: IPostService = Depends(get_post_service),
):
    """根据提要润色生成帖子"""
    result = service.generate(
        theme_id=request.theme_id,
        summary=request.summary,
        requirements=request.requirements,
        post_length=request.post_length,
        use_api=request.use_api,
        api_type=request.api_type
    )
    return PostResponse(**result)


@router.post("/", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    service: IPostService = Depends(get_post_service),
):
    """手动创建帖子"""
    result = service.create(
        theme_id=post_data.theme_id,
        content=post_data.content,
        summary=post_data.summary,
        requirements=post_data.requirements
    )
    return PostResponse(**result)


@router.get("/", response_model=PostListResponse)
async def list_posts(
    theme_id: int = Query(None, description="按主题筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: IPostService = Depends(get_post_service),
):
    """获取帖子列表"""
    result = service.get_all(theme_id, skip, limit)
    return PostListResponse(
        posts=[PostResponse(**p) for p in result["posts"]],
        total=result["total"]
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    service: IPostService = Depends(get_post_service),
):
    """获取单个帖子详情"""
    result = service.get_by_id(post_id)
    return PostResponse(**result)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    update_data: PostUpdate,
    service: IPostService = Depends(get_post_service),
):
    """更新帖子内容"""
    result = service.update(
        post_id,
        content=update_data.content,
        summary=update_data.summary,
        requirements=update_data.requirements
    )
    return PostResponse(**result)


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    service: IPostService = Depends(get_post_service),
):
    """删除帖子"""
    service.delete(post_id)
    return {"message": "帖子已删除"}
