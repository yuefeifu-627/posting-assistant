"""Schema 验证测试"""

import pytest
from datetime import datetime
from app.schemas import (
    ThemeCreate,
    ThemeUpdate,
    ThemeResponse,
    GeneratePostRequest,
    PostCreate,
    PostUpdate,
    UserPostCreate,
    UserPostUpdate,
)


class TestThemeSchemas:
    """主题 Schema 测试"""

    def test_theme_create_valid(self):
        """测试有效的主题创建"""
        data = ThemeCreate(name="通勤体验分享", post_length=500)
        assert data.name == "通勤体验分享"
        assert data.post_length == 500

    def test_theme_create_default_length(self):
        """测试主题创建默认字数"""
        data = ThemeCreate(name="默认字数主题")
        assert data.post_length == 500

    def test_theme_create_invalid_name(self):
        """测试无效的主题名称"""
        # 太短
        with pytest.raises(ValueError, match="不能少于"):
            ThemeCreate(name="a")

        # 包含非法字符
        with pytest.raises(ValueError, match="只能包含"):
            ThemeCreate(name="主题<script>")

        # 纯数字
        with pytest.raises(ValueError, match="不能仅为数字"):
            ThemeCreate(name="12345")

    def test_theme_create_invalid_length(self):
        """测试无效的字数"""
        # 太小
        with pytest.raises(ValueError, match="100 到 2000"):
            ThemeCreate(name="主题", post_length=50)

        # 太大
        with pytest.raises(ValueError, match="100 到 2000"):
            ThemeCreate(name="主题", post_length=3000)

    def test_theme_update_valid(self):
        """测试有效的主题更新"""
        data = ThemeUpdate(name="更新后的名称", post_length=800)
        assert data.name == "更新后的名称"
        assert data.post_length == 800

    def test_theme_update_partial(self):
        """测试部分更新主题"""
        data = ThemeUpdate(name="只更新名称")
        assert data.name == "只更新名称"
        assert data.post_length is None

    def test_theme_update_no_fields(self):
        """测试没有字段的更新"""
        with pytest.raises(ValueError, match="至少需要一个"):
            ThemeUpdate()

    def test_theme_response(self):
        """测试主题响应"""
        now = datetime.now()
        data = ThemeResponse(
            id=1,
            name="主题",
            post_length=500,
            created_at=now,
            updated_at=now,
            post_count=10
        )
        assert data.id == 1
        assert data.name == "主题"
        assert data.post_count == 10


class TestPostSchemas:
    """帖子 Schema 测试"""

    def test_generate_post_request_valid(self):
        """测试有效的生成帖子请求"""
        data = GeneratePostRequest(
            theme_id=1,
            summary="1. 驾驶感受\n2. 油耗表现",
            post_length=500,
            use_api=False
        )
        assert data.theme_id == 1
        assert data.summary == "1. 驾驶感受\n2. 油耗表现"
        assert data.use_api is False

    def test_generate_post_invalid_theme_id(self):
        """测试无效的主题 ID"""
        with pytest.raises(ValueError, match="正整数"):
            GeneratePostRequest(theme_id=0, summary="test")

        with pytest.raises(ValueError, match="正整数"):
            GeneratePostRequest(theme_id=-1, summary="test")

    def test_generate_post_invalid_summary(self):
        """测试无效的摘要"""
        # 太短
        with pytest.raises(ValueError):
            GeneratePostRequest(theme_id=1, summary="a")

        # 包含 XSS
        with pytest.raises(ValueError, match="不安全的"):
            GeneratePostRequest(theme_id=1, summary="<script>alert(1)</script>")

    def test_generate_post_invalid_post_length(self):
        """测试无效的字数"""
        with pytest.raises(ValueError, match="不能少于"):
            GeneratePostRequest(theme_id=1, summary="valid summary", post_length=50)

        with pytest.raises(ValueError, match="不能超过"):
            GeneratePostRequest(theme_id=1, summary="valid summary", post_length=3000)

    def test_post_create_valid(self):
        """测试有效的帖子创建"""
        data = PostCreate(
            theme_id=1,
            content="这是一篇完整的帖子内容。\n\n这里有多行内容...",
            summary="简短摘要",
            requirements="字数要求"
        )
        assert data.theme_id == 1
        assert len(data.content) > 10

    def test_post_create_invalid_content(self):
        """测试无效的帖子内容"""
        # 太短
        with pytest.raises(ValueError, match="过于简短"):
            PostCreate(theme_id=1, content="太短了")

        # 过多重复
        with pytest.raises(ValueError, match="过多重复"):
            PostCreate(theme_id=1, content="test " * 50)

    def test_post_update_valid(self):
        """测试有效的帖子更新"""
        data = PostUpdate(content="更新后的内容")
        assert data.content == "更新后的内容"
        assert data.summary is None

    def test_post_update_no_fields(self):
        """测试没有字段的更新"""
        with pytest.raises(ValueError, match="至少需要一个"):
            PostUpdate()


class TestUserPostSchemas:
    """用户帖子 Schema 测试"""

    def test_user_post_create_valid(self):
        """测试有效的用户帖子创建"""
        data = UserPostCreate(
            title="我的用车经验",
            content="这是一篇关于用车的详细分享...",
            tags="通勤,油耗,空间",
            note="这是一篇优质帖子"
        )
        assert data.title == "我的用车经验"
        assert data.tags == "通勤,油耗,空间"
        assert data.note == "这是一篇优质帖子"

    def test_user_post_create_minimal(self):
        """测试最小化的用户帖子创建"""
        data = UserPostCreate(content="至少需要内容")
        assert data.content == "至少需要内容"
        assert data.title is None
        assert data.tags is None
        assert data.note is None

    def test_user_post_create_invalid_title(self):
        """测试无效的标题"""
        with pytest.raises(ValueError, match="不安全的"):
            UserPostCreate(
                title="<script>alert(1)</script>",
                content="valid content"
            )

    def test_user_post_create_invalid_content(self):
        """测试无效的内容"""
        with pytest.raises(ValueError, match="过于简短"):
            UserPostCreate(content="太短")

    def test_user_post_update_valid(self):
        """测试有效的用户帖子更新"""
        data = UserPostUpdate(
            title="新标题",
            content="新内容",
            tags="新标签"
        )
        assert data.title == "新标题"
        assert data.content == "新内容"
        assert data.tags == "新标签"

    def test_user_post_update_no_fields(self):
        """测试没有字段的更新"""
        with pytest.raises(ValueError, match="至少需要一个"):
            UserPostUpdate()


class TestSchemaEdgeCases:
    """Schema 边界情况测试"""

    def test_max_length_boundary(self):
        """测试最大长度边界"""
        # 主题名称最大长度
        long_name = "a" * 255
        data = ThemeCreate(name=long_name)
        assert len(data.name) == 255

        # 超过最大长度
        too_long_name = "a" * 256
        with pytest.raises(ValueError, match="不能超过"):
            ThemeCreate(name=too_long_name)

    def test_min_length_boundary(self):
        """测试最小长度边界"""
        # 摘要最小长度
        data = GeneratePostRequest(theme_id=1, summary="ab")
        assert len(data.summary) == 2

        # 低于最小长度
        with pytest.raises(ValueError, match="不能少于"):
            GeneratePostRequest(theme_id=1, summary="a")

    def test_post_length_boundary(self):
        """测试字数边界"""
        # 最小字数
        data1 = GeneratePostRequest(theme_id=1, summary="valid", post_length=100)
        assert data1.post_length == 100

        # 最大字数
        data2 = GeneratePostRequest(theme_id=1, summary="valid", post_length=2000)
        assert data2.post_length == 2000

    def test_special_characters_in_content(self):
        """测试内容中的特殊字符"""
        # 正常的特殊字符应该被保留（经过 HTML 转义）
        data = PostCreate(
            theme_id=1,
            content="这是内容，包含逗号，句号。引号\"和单引号'"
        )
        assert "," in data.content
        assert "。" in data.content

    def test_whitespace_handling(self):
        """测试空白字符处理"""
        data = ThemeCreate(name="  多余空格的主题  ")
        # 应该清理空白字符
        assert "  " not in data.name
        assert data.name == "多余空格的主题"
