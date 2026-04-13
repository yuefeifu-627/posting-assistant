"""业务规则验证器"""

import re
from typing import Optional
from app.validators.string_validator import (
    validate_text_content,
    clean_whitespace,
    detect_xss,
    sanitize_sql_input,
    sanitize_html,
)


# 主题名称允许的字符模式（中文、英文、数字、空格、常见标点）
THEME_NAME_PATTERN = r'^[\u4e00-\u9fa5a-zA-Z0-9\s\-_,，。、！？!?]+$'


def validate_theme_name(name: str) -> str:
    """
    验证主题名称

    Args:
        name: 主题名称

    Returns:
        验证和清理后的名称

    Raises:
        ValueError: 如果验证失败
    """
    # 基本验证
    name = validate_text_content(
        name,
        min_length=2,
        max_length=255,
        check_xss=False,
        check_sql_injection=False,
        strip_html=False,
    )

    # 清理空白
    name = clean_whitespace(name)

    # 检查字符模式
    if not re.match(THEME_NAME_PATTERN, name):
        raise ValueError(
            "主题名称只能包含中文、英文、数字和常见标点符号"
        )

    # 检查是否为纯数字或纯标点
    if re.match(r'^[\d\-_,，。、！？!?]+$', name):
        raise ValueError("主题名称不能仅为数字或标点符号")

    return name


def validate_post_content(content: str) -> str:
    """
    验证帖子内容

    Args:
        content: 帖子内容

    Returns:
        验证和清理后的内容

    Raises:
        ValueError: 如果验证失败
    """
    # 清理行首行尾空白，但保留空行和基本格式
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        # 清理每行的前导/尾随空白
        cleaned_line = line.rstrip()
        cleaned_lines.append(cleaned_line)

    # 重新组合，保留原始换行
    content = '\n'.join(cleaned_lines)

    # 长度检查
    text_length = len(content)
    if text_length < 10:
        raise ValueError("内容过于简短，至少需要10个字符")
    if text_length > 10000:
        raise ValueError("内容过长，不能超过10000个字符")

    # XSS 检查
    if detect_xss(content):
        raise ValueError("内容包含不安全的 HTML 内容")

    # SQL 注入检查
    content = sanitize_sql_input(content)

    # HTML 转义
    content = sanitize_html(content)

    # 检查是否包含过多重复字符（防止垃圾内容）
    if _has_excessive_repetition(content):
        raise ValueError("内容包含过多重复字符，请提供更有意义的内容")

    # 检查基本结构
    lines = [line for line in content.split('\n') if line.strip()]
    if len(lines) < 2:
        raise ValueError("内容过于简短，请提供更完整的帖子内容")

    return content


def validate_summary(summary: str, max_length: int = 5000) -> str:
    """
    验证内容提要

    Args:
        summary: 内容提要
        max_length: 最大长度

    Returns:
        验证和清理后的提要

    Raises:
        ValueError: 如果验证失败
    """
    # 基本验证
    summary = validate_text_content(
        summary,
        min_length=2,
        max_length=max_length,
        check_xss=True,
        check_sql_injection=True,
        strip_html=True,
    )

    # 清理空白
    summary = clean_whitespace(summary)

    # 检查是否包含过多重复
    if _has_excessive_repetition(summary, threshold=0.5):
        raise ValueError("提要包含过多重复内容")

    return summary


def validate_requirements(requirements: Optional[str]) -> Optional[str]:
    """
    验证任务要求

    Args:
        requirements: 任务要求（可选）

    Returns:
        验证和清理后的要求，如果为 None 则返回 None

    Raises:
        ValueError: 如果验证失败
    """
    if requirements is None:
        return None

    # 基本验证
    requirements = validate_text_content(
        requirements,
        min_length=1,
        max_length=2000,
        check_xss=True,
        check_sql_injection=True,
        strip_html=True,
    )

    # 清理空白
    requirements = clean_whitespace(requirements)

    return requirements


def validate_post_length(length: int, theme_default: Optional[int] = None) -> int:
    """
    验证帖子字数要求

    Args:
        length: 请求的字数
        theme_default: 主题默认字数（可选）

    Returns:
        验证后的字数

    Raises:
        ValueError: 如果验证失败
    """
    if not isinstance(length, int):
        raise ValueError("字数必须是整数")

    min_length = 100
    max_length = 2000

    if length < min_length:
        raise ValueError(f"字数不能少于 {min_length}")
    if length > max_length:
        raise ValueError(f"字数不能超过 {max_length}")

    # 如果提供了主题默认字数，检查是否合理
    if theme_default is not None:
        ratio = length / theme_default
        if ratio < 0.5 or ratio > 3.0:
            raise ValueError(f"请求字数与主题设置差异过大（主题默认: {theme_default}）")

    return length


def validate_vehicle_model(model: str) -> str:
    """
    验证车型配置

    Args:
        model: 车型字符串

    Returns:
        验证后的车型
    """
    if not model:
        raise ValueError("车型配置不能为空")

    return validate_text_content(
        model,
        min_length=2,
        max_length=100,
        check_xss=False,
        check_sql_injection=False,
        strip_html=False,
    )


def validate_ai_temperature(temperature: float) -> float:
    """
    验证 AI 温度参数

    Args:
        temperature: 温度值

    Returns:
        验证后的温度值

    Raises:
        ValueError: 如果验证失败
    """
    if not isinstance(temperature, (int, float)):
        raise ValueError("温度必须是数字")

    if temperature < 0.0 or temperature > 2.0:
        raise ValueError("温度值必须在 0.0 到 2.0 之间")

    return float(temperature)


def validate_max_tokens(max_tokens: int) -> int:
    """
    验证最大 token 数

    Args:
        max_tokens: 最大 token 数

    Returns:
        验证后的 token 数

    Raises:
        ValueError: 如果验证失败
    """
    if not isinstance(max_tokens, int):
        raise ValueError("max_tokens 必须是整数")

    if max_tokens < 1 or max_tokens > 32768:
        raise ValueError("max_tokens 必须在 1 到 32768 之间")

    return max_tokens


def _has_excessive_repetition(text: str, threshold: float = 0.4) -> bool:
    """
    检测文本是否包含过多重复内容

    Args:
        text: 待检测的文本
        threshold: 重复阈值（0-1），超过此值认为重复过多

    Returns:
        如果重复过多返回 True
    """
    if len(text) < 10:
        return False

    # 分割成单词/字符
    words = re.findall(r'[\w\u4e00-\u9fa5]+', text.lower())
    if len(words) < 3:
        return False

    # 计算重复率
    unique_words = set(words)
    repetition_ratio = 1 - (len(unique_words) / len(words))

    return repetition_ratio > threshold
