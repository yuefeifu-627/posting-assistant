"""字符串验证和清理工具"""

import re
import html
from typing import Optional, List


# SQL 注入关键词模式
SQL_INJECTION_PATTERNS = [
    r'(\bOR\b|\bAND\b)\s+\d+\s*=\s*\d+',  # OR 1=1, AND 1=1
    r"'\s*OR\s*'",  # ' OR '
    r'"\s*OR\s*"',  # " OR "
    r"'\s*AND\s*'",  # ' AND '
    r'"\s*AND\s*"',  # " AND "
    r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)\b",  # SQL 关键字
    r"--\s*$",  # SQL 注释
    r"/\*.*?\*/",  # SQL 块注释
    r";\s*\w+",  # 分号后跟命令
    r"'\s*(?:--|$)",  # 单引号注入
    r'"\s*(?:--|$)',  # 双引号注入
]

# XSS 攻击模式
XSS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # script 标签
    r'on\w+\s*=',  # 事件处理器 (onclick, onerror 等)
    r'javascript:',  # javascript: 协议
    r'<iframe[^>]*>',  # iframe 标签
    r'<object[^>]*>',  # object 标签
    r'<embed[^>]*>',  # embed 标签
    r'<link[^>]*>',  # link 标签
    r'<meta[^>]*>',  # meta 标签
]


def sanitize_html(text: str) -> str:
    """
    转义 HTML 特殊字符，防止 XSS 攻击

    Args:
        text: 待转义的文本

    Returns:
        转义后的安全文本
    """
    return html.escape(text, quote=True)


def detect_xss(text: str) -> bool:
    """
    检测文本中是否包含潜在的 XSS 攻击

    Args:
        text: 待检测的文本

    Returns:
        如果检测到 XSS 模式返回 True
    """
    text_lower = text.lower()
    for pattern in XSS_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL):
            return True
    return False


def detect_sql_injection(text: str) -> bool:
    """
    检测文本中是否包含潜在的 SQL 注入

    Args:
        text: 待检测的文本

    Returns:
        如果检测到 SQL 注入模式返回 True
    """
    text_upper = text.upper()
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text_upper, re.IGNORECASE):
            return True
    return False


def sanitize_sql_input(text: str) -> str:
    """
    清理 SQL 输入，移除危险的 SQL 语句

    Args:
        text: 待清理的文本

    Returns:
        清理后的安全文本

    Raises:
        ValueError: 如果检测到严重的 SQL 注入尝试
    """
    if detect_sql_injection(text):
        raise ValueError("输入包含潜在的 SQL 注入")

    # 移除多余的分号
    text = re.sub(r';\s*$', '', text)

    # 移除 SQL 注释
    text = re.sub(r'--.*?$', '', text, flags=re.MULTILINE)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

    return text.strip()


def clean_whitespace(text: str) -> str:
    """
    清理文本中的空白字符

    Args:
        text: 待清理的文本

    Returns:
        清理后的文本
    """
    # 替换多个空格为单个空格
    text = re.sub(r' +', ' ', text)
    # 替换多个换行为单个换行
    text = re.sub(r'\n+', '\n', text)
    # 替换多个制表符为单个制表符
    text = re.sub(r'\t+', '\t', text)
    # 移除首尾空白
    return text.strip()


def validate_text_content(
    text: str,
    min_length: int = 1,
    max_length: int = 10000,
    allow_empty: bool = False,
    check_xss: bool = True,
    check_sql_injection: bool = True,
    strip_html: bool = True,
) -> str:
    """
    验证文本内容，包括长度、安全性检查

    Args:
        text: 待验证的文本
        min_length: 最小长度
        max_length: 最大长度
        allow_empty: 是否允许空值
        check_xss: 是否检查 XSS
        check_sql_injection: 是否检查 SQL 注入
        strip_html: 是否转义 HTML

    Returns:
        验证和清理后的文本

    Raises:
        ValueError: 如果验证失败
    """
    if not text:
        if not allow_empty:
            raise ValueError("文本内容不能为空")
        return text

    # 清理空白字符
    text = clean_whitespace(text)

    # 长度检查
    text_length = len(text)
    if text_length < min_length:
        raise ValueError(f"文本长度不能少于 {min_length} 个字符")
    if text_length > max_length:
        raise ValueError(f"文本长度不能超过 {max_length} 个字符")

    # XSS 检查
    if check_xss and detect_xss(text):
        raise ValueError("文本包含不安全的 HTML 内容")

    # SQL 注入检查
    if check_sql_injection:
        text = sanitize_sql_input(text)

    # HTML 转义
    if strip_html:
        text = sanitize_html(text)

    return text


def validate_list_items(
    items: List[str],
    item_min_length: int = 1,
    item_max_length: int = 255,
    max_items: int = 100,
) -> List[str]:
    """
    验证字符串列表

    Args:
        items: 待验证的列表
        item_min_length: 每个项目的最小长度
        item_max_length: 每个项目的最大长度
        max_items: 最大项目数量

    Returns:
        验证和清理后的列表

    Raises:
        ValueError: 如果验证失败
    """
    if not isinstance(items, list):
        raise ValueError("必须是列表类型")

    if len(items) > max_items:
        raise ValueError(f"项目数量不能超过 {max_items} 个")

    validated = []
    for item in items:
        if not isinstance(item, str):
            raise ValueError("列表项必须是字符串")
        validated_item = validate_text_content(
            item,
            min_length=item_min_length,
            max_length=item_max_length,
            check_xss=False,
            check_sql_injection=False,
            strip_html=False,
        )
        validated.append(validated_item)

    return validated
