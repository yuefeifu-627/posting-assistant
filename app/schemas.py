"""Pydantic 模型定义 - 带增强验证"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from app.validators import (
    validate_theme_name,
    validate_post_content,
    validate_summary,
    validate_requirements,
    validate_post_length,
    validate_text_content,
)


# === 主题相关 ===

class ThemeCreate(BaseModel):
    """创建主题模型"""
    name: str = Field(..., description="主题名称")
    post_length: int = Field(default=500, description="发帖字数")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证主题名称"""
        return validate_theme_name(v)

    @field_validator('post_length')
    @classmethod
    def validate_length(cls, v: int) -> int:
        """验证字数限制"""
        if not isinstance(v, int):
            raise ValueError("字数必须是整数")
        if v < 100 or v > 2000:
            raise ValueError("字数必须在 100 到 2000 之间")
        return v


class ThemeUpdate(BaseModel):
    """更新主题模型"""
    name: Optional[str] = Field(None, description="主题名称")
    post_length: Optional[int] = Field(None, description="发帖字数")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """验证主题名称"""
        if v is not None:
            return validate_theme_name(v)
        return v

    @field_validator('post_length')
    @classmethod
    def validate_length(cls, v: Optional[int]) -> Optional[int]:
        """验证字数限制"""
        if v is not None:
            if not isinstance(v, int):
                raise ValueError("字数必须是整数")
            if v < 100 or v > 2000:
                raise ValueError("字数必须在 100 到 2000 之间")
            return v
        return v

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if self.name is None and self.post_length is None:
            raise ValueError("至少需要提供一个字段进行更新")
        return self


class ThemeResponse(BaseModel):
    """主题响应模型"""
    id: int
    name: str
    post_length: int
    created_at: datetime
    updated_at: datetime
    post_count: int = 0

    class Config:
        from_attributes = True


class ThemeListResponse(BaseModel):
    """主题列表响应模型"""
    themes: List[ThemeResponse]
    total: int


# === 帖子相关 ===

class GeneratePostRequest(BaseModel):
    """生成帖子请求模型"""
    theme_id: int = Field(..., description="主题ID")
    summary: str = Field(..., description="内容提要，用户提供的要点/大纲")
    requirements: Optional[str] = Field(None, description="主办方的任务要求")
    post_length: Optional[int] = Field(None, description="发帖字数")
    use_api: bool = Field(default=False, description="是否使用云端API")
    api_type: str = Field(default="glm", description="API类型 (glm/minmax)")

    @field_validator('theme_id')
    @classmethod
    def validate_theme_id(cls, v: int) -> int:
        """验证主题ID"""
        if not isinstance(v, int) or v <= 0:
            raise ValueError("主题ID必须是正整数")
        return v

    @field_validator('summary')
    @classmethod
    def validate_summary_field(cls, v: str) -> str:
        """验证内容提要"""
        return validate_summary(v)

    @field_validator('requirements')
    @classmethod
    def validate_requirements_field(cls, v: Optional[str]) -> Optional[str]:
        """验证任务要求"""
        if v is not None:
            return validate_requirements(v)
        return v

    @field_validator('post_length')
    @classmethod
    def validate_post_length_field(cls, v: Optional[int]) -> Optional[int]:
        """验证字数限制"""
        if v is not None:
            return validate_post_length(v)
        return v


class PostCreate(BaseModel):
    """手动创建帖子模型"""
    theme_id: int = Field(..., description="主题ID")
    content: str = Field(..., description="帖子内容")
    summary: Optional[str] = Field(None, description="内容提要")
    requirements: Optional[str] = Field(None, description="任务要求")

    @field_validator('theme_id')
    @classmethod
    def validate_theme_id(cls, v: int) -> int:
        """验证主题ID"""
        if not isinstance(v, int) or v <= 0:
            raise ValueError("主题ID必须是正整数")
        return v

    @field_validator('content')
    @classmethod
    def validate_content_field(cls, v: str) -> str:
        """验证帖子内容"""
        return validate_post_content(v)

    @field_validator('summary')
    @classmethod
    def validate_summary_field(cls, v: Optional[str]) -> Optional[str]:
        """验证内容提要"""
        if v is not None:
            return validate_summary(v)
        return v

    @field_validator('requirements')
    @classmethod
    def validate_requirements_field(cls, v: Optional[str]) -> Optional[str]:
        """验证任务要求"""
        if v is not None:
            return validate_requirements(v)
        return v


class PostUpdate(BaseModel):
    """更新帖子模型"""
    content: Optional[str] = Field(None, description="帖子内容")
    summary: Optional[str] = Field(None, description="内容提要")
    requirements: Optional[str] = Field(None, description="任务要求")

    @field_validator('content')
    @classmethod
    def validate_content_field(cls, v: Optional[str]) -> Optional[str]:
        """验证帖子内容"""
        if v is not None:
            return validate_post_content(v)
        return v

    @field_validator('summary')
    @classmethod
    def validate_summary_field(cls, v: Optional[str]) -> Optional[str]:
        """验证内容提要"""
        if v is not None:
            return validate_summary(v)
        return v

    @field_validator('requirements')
    @classmethod
    def validate_requirements_field(cls, v: Optional[str]) -> Optional[str]:
        """验证任务要求"""
        if v is not None:
            return validate_requirements(v)
        return v

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if self.content is None and self.summary is None and self.requirements is None:
            raise ValueError("至少需要提供一个字段进行更新")
        return self


class PostResponse(BaseModel):
    """帖子响应模型"""
    id: int
    theme_id: int
    theme_name: str = ""
    summary: Optional[str]
    requirements: Optional[str]
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """帖子列表响应模型"""
    posts: List[PostResponse]
    total: int


# === 用户语料库相关 ===

class UserPostCreate(BaseModel):
    """创建用户帖子模型"""
    title: Optional[str] = Field(None, description="帖子标题/主题")
    content: str = Field(..., description="帖子内容")
    tags: Optional[str] = Field(None, description="标签，用逗号分隔")
    note: Optional[str] = Field(None, description="备注")

    @field_validator('title')
    @classmethod
    def validate_title_field(cls, v: Optional[str]) -> Optional[str]:
        """验证标题"""
        if v is not None:
            return validate_text_content(
                v,
                min_length=1,
                max_length=255,
                check_xss=True,
                check_sql_injection=True,
                strip_html=True,
            )
        return v

    @field_validator('content')
    @classmethod
    def validate_content_field(cls, v: str) -> str:
        """验证内容"""
        return validate_post_content(v)

    @field_validator('tags')
    @classmethod
    def validate_tags_field(cls, v: Optional[str]) -> Optional[str]:
        """验证标签"""
        if v is not None:
            return validate_text_content(
                v,
                min_length=1,
                max_length=255,
                check_xss=True,
                check_sql_injection=True,
                strip_html=True,
            )
        return v

    @field_validator('note')
    @classmethod
    def validate_note_field(cls, v: Optional[str]) -> Optional[str]:
        """验证备注"""
        if v is not None:
            return validate_text_content(
                v,
                min_length=1,
                max_length=1000,
                check_xss=True,
                check_sql_injection=True,
                strip_html=True,
            )
        return v


class UserPostUpdate(BaseModel):
    """更新用户帖子模型"""
    title: Optional[str] = Field(None, description="帖子标题/主题")
    content: Optional[str] = Field(None, description="帖子内容")
    tags: Optional[str] = Field(None, description="标签，用逗号分隔")
    note: Optional[str] = Field(None, description="备注")

    @field_validator('title')
    @classmethod
    def validate_title_field(cls, v: Optional[str]) -> Optional[str]:
        """验证标题"""
        if v is not None:
            return validate_text_content(
                v,
                min_length=1,
                max_length=255,
                check_xss=True,
                check_sql_injection=True,
                strip_html=True,
            )
        return v

    @field_validator('content')
    @classmethod
    def validate_content_field(cls, v: Optional[str]) -> Optional[str]:
        """验证内容"""
        if v is not None:
            return validate_post_content(v)
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags_field(cls, v: Optional[str]) -> Optional[str]:
        """验证标签"""
        if v is not None:
            return validate_text_content(
                v,
                min_length=1,
                max_length=255,
                check_xss=True,
                check_sql_injection=True,
                strip_html=True,
            )
        return v

    @field_validator('note')
    @classmethod
    def validate_note_field(cls, v: Optional[str]) -> Optional[str]:
        """验证备注"""
        if v is not None:
            return validate_text_content(
                v,
                min_length=1,
                max_length=1000,
                check_xss=True,
                check_sql_injection=True,
                strip_html=True,
            )
        return v

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if all(v is None for v in [self.title, self.content, self.tags, self.note]):
            raise ValueError("至少需要提供一个字段进行更新")
        return self


class UserPostResponse(BaseModel):
    """用户帖子响应模型"""
    id: int
    title: Optional[str]
    content: str
    tags: Optional[str]
    note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPostListResponse(BaseModel):
    """用户帖子列表响应模型"""
    posts: List[UserPostResponse]
    total: int


# === 用户认证相关 ===

class UserRegister(BaseModel):
    """用户注册模型"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")
    nickname: Optional[str] = Field(None, description="昵称")
    email: Optional[str] = Field(None, description="邮箱")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """验证手机号"""
        import re
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError("请输入有效的手机号")
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码"""
        if len(v) < 6:
            raise ValueError("密码长度不能少于6位")
        if len(v) > 20:
            raise ValueError("密码长度不能超过20位")
        return v

    @field_validator('nickname')
    @classmethod
    def validate_nickname(cls, v: Optional[str]) -> Optional[str]:
        """验证昵称"""
        if v is not None:
            if len(v) < 2 or len(v) > 20:
                raise ValueError("昵称长度必须在2-20个字符之间")
        return v


class UserLogin(BaseModel):
    """用户登录模型"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """验证手机号"""
        import re
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError("请输入有效的手机号")
        return v


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    phone: str
    nickname: Optional[str]
    email: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str
    expires_in: int  # 过期时间（秒）
