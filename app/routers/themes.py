"""主题路由"""

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_theme_service
from app.di import IThemeService
from app.schemas import (
    ThemeCreate,
    ThemeUpdate,
    ThemeResponse,
    ThemeListResponse
)

router = APIRouter(prefix="/api/themes", tags=["themes"])


@router.post("/", response_model=ThemeResponse)
async def create_theme(
    theme_data: ThemeCreate,
    service: IThemeService = Depends(get_theme_service),
):
    """创建新主题"""
    result = service.create(theme_data.name, theme_data.post_length)
    return ThemeResponse(**result)


@router.get("/", response_model=ThemeListResponse)
async def list_themes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: IThemeService = Depends(get_theme_service),
):
    """获取主题列表"""
    result = service.get_all(skip, limit)
    return ThemeListResponse(
        themes=[ThemeResponse(**t) for t in result["themes"]],
        total=result["total"]
    )


@router.get("/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    theme_id: int,
    service: IThemeService = Depends(get_theme_service),
):
    """获取单个主题详情"""
    result = service.get_by_id(theme_id)
    return ThemeResponse(**result)


@router.put("/{theme_id}", response_model=ThemeResponse)
async def update_theme(
    theme_id: int,
    update_data: ThemeUpdate,
    service: IThemeService = Depends(get_theme_service),
):
    """更新主题"""
    result = service.update(
        theme_id,
        name=update_data.name,
        post_length=update_data.post_length
    )
    return ThemeResponse(**result)


@router.delete("/{theme_id}")
async def delete_theme(
    theme_id: int,
    service: IThemeService = Depends(get_theme_service),
):
    """删除主题及其所有帖子"""
    service.delete(theme_id)
    return {"message": "主题及其帖子已删除"}
