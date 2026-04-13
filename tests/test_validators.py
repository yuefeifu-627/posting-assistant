"""验证器测试"""

import pytest
from app.validators import (
    sanitize_html,
    sanitize_sql_input,
    validate_text_content,
    clean_whitespace,
    validate_theme_name,
    validate_post_content,
    validate_summary,
    validate_requirements,
    validate_post_length,
    validate_ai_temperature,
    validate_max_tokens,
)
from app.validators.string_validator import detect_xss, detect_sql_injection


class TestStringValidators:
    """字符串验证器测试"""

    def test_sanitize_html(self):
        """测试 HTML 转义"""
        # 注意：html.escape 会将单引号转义为 &#x27;
        assert sanitize_html("<script>alert('xss')</script>") == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
        assert sanitize_html("Hello & World") == "Hello &amp; World"
        assert sanitize_html("Normal text") == "Normal text"

    def test_detect_xss(self):
        """测试 XSS 检测"""
        assert detect_xss("<script>alert('xss')</script>") is True
        assert detect_xss("<div onclick='malicious()'>") is True
        assert detect_xss("javascript:alert(1)") is True
        assert detect_xss("Normal text") is False
        assert detect_xss("This is <b>bold</b>") is False

    def test_detect_sql_injection(self):
        """测试 SQL 注入检测"""
        assert detect_sql_injection("1' OR '1'='1") is True
        assert detect_sql_injection("1; DROP TABLE users--") is True
        assert detect_sql_injection("SELECT * FROM users") is True
        assert detect_sql_injection("Normal text") is False

    def test_sanitize_sql_input(self):
        """测试 SQL 输入清理"""
        assert sanitize_sql_input("Normal text") == "Normal text"
        assert sanitize_sql_input("Text with semicolon;") == "Text with semicolon"
        # 检测到注入时应该抛出异常
        with pytest.raises(ValueError, match="SQL 注入"):
            sanitize_sql_input("1' OR '1'='1")

    def test_clean_whitespace(self):
        """测试空白字符清理"""
        assert clean_whitespace("  Hello   World  ") == "Hello World"
        assert clean_whitespace("Line1\n\nLine2\n\n\nLine3") == "Line1\nLine2\nLine3"
        assert clean_whitespace("Text\t\twith\ttabs") == "Text\twith\ttabs"

    def test_validate_text_content(self):
        """测试文本内容验证"""
        # 正常情况
        result = validate_text_content("Valid text", min_length=1, max_length=100)
        assert result == "Valid text"

        # 长度不足
        with pytest.raises(ValueError, match="不能少于"):
            validate_text_content("ab", min_length=5)

        # 长度过长
        with pytest.raises(ValueError, match="不能超过"):
            validate_text_content("a" * 200, max_length=100)

        # XSS 检测
        with pytest.raises(ValueError, match="不安全的 HTML"):
            validate_text_content("<script>alert(1)</script>", check_xss=True)


class TestBusinessValidators:
    """业务验证器测试"""

    def test_validate_theme_name(self):
        """测试主题名称验证"""
        # 正常情况
        assert validate_theme_name("通勤经验分享") == "通勤经验分享"
        assert validate_theme_name("City Driving Experience") == "City Driving Experience"

        # 名称太短
        with pytest.raises(ValueError):
            validate_theme_name("a")

        # 非法字符
        with pytest.raises(ValueError, match="只能包含"):
            validate_theme_name("主题<script>")

        # 纯数字
        with pytest.raises(ValueError, match="不能仅为数字"):
            validate_theme_name("12345")

    def test_validate_post_content(self):
        """测试帖子内容验证"""
        # 正常情况
        content = "这是一篇关于用车体验的帖子。\n\n首先，我想分享我的驾驶感受..."
        result = validate_post_content(content)
        assert result == content

        # 内容太短
        with pytest.raises(ValueError, match="过于简短"):
            validate_post_content("太短了")

        # 过多重复
        with pytest.raises(ValueError, match="过多重复"):
            validate_post_content("a " * 100)

    def test_validate_summary(self):
        """测试提要验证"""
        # 正常情况
        summary = "1. 驾驶感受\n2. 油耗表现\n3. 空间体验"
        result = validate_summary(summary)
        assert result == summary

        # 太短
        with pytest.raises(ValueError):
            validate_summary("a")

        # 太长
        with pytest.raises(ValueError, match="不能超过"):
            validate_summary("a" * 6000, max_length=5000)

    def test_validate_requirements(self):
        """测试任务要求验证"""
        # None 应该返回 None
        assert validate_requirements(None) is None

        # 正常情况
        result = validate_requirements("字数500字左右，风格自然")
        assert result == "字数500字左右，风格自然"

    def test_validate_post_length(self):
        """测试字数验证"""
        # 正常情况
        assert validate_post_length(500) == 500
        assert validate_post_length(100) == 100
        assert validate_post_length(2000) == 2000

        # 太短
        with pytest.raises(ValueError, match="不能少于"):
            validate_post_length(50)

        # 太长
        with pytest.raises(ValueError, match="不能超过"):
            validate_post_length(3000)

        # 不是整数
        with pytest.raises(ValueError, match="必须是整数"):
            validate_post_length(500.5)

    def test_validate_ai_temperature(self):
        """测试 AI 温度验证"""
        # 正常情况
        assert validate_ai_temperature(0.5) == 0.5
        assert validate_ai_temperature(0.0) == 0.0
        assert validate_ai_temperature(1.0) == 1.0

        # 太低
        with pytest.raises(ValueError, match="0.0 到 2.0"):
            validate_ai_temperature(-0.1)

        # 太高
        with pytest.raises(ValueError, match="0.0 到 2.0"):
            validate_ai_temperature(2.5)

    def test_validate_max_tokens(self):
        """测试 max_tokens 验证"""
        # 正常情况
        assert validate_max_tokens(100) == 100
        assert validate_max_tokens(4096) == 4096

        # 太小
        with pytest.raises(ValueError, match="1 到 32768"):
            validate_max_tokens(0)

        # 太大
        with pytest.raises(ValueError, match="1 到 32768"):
            validate_max_tokens(50000)
