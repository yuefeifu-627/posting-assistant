"""自定义异常类"""


class AppException(Exception):
    """应用基础异常"""

    def __init__(self, message: str, code: str = "UNKNOWN"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(AppException):
    """资源不存在"""

    def __init__(self, resource: str, id: int = None):
        message = f"{resource}不存在" if id is None else f"{resource}不存在 (ID: {id})"
        super().__init__(message, code="NOT_FOUND")


class ThemeNotFound(NotFoundError):
    """主题不存在"""

    def __init__(self, id: int = None):
        super().__init__("主题", id)


class PostNotFound(NotFoundError):
    """帖子不存在"""

    def __init__(self, id: int = None):
        super().__init__("帖子", id)


class UserPostNotFound(NotFoundError):
    """用户帖子不存在"""

    def __init__(self, id: int = None):
        super().__init__("用户帖子", id)


class DuplicateError(AppException):
    """重复资源"""

    def __init__(self, resource: str, field: str = "名称"):
        super().__init__(f"{resource}{field}已存在", code="DUPLICATE")


class ThemeDuplicate(DuplicateError):
    """主题名称重复"""

    def __init__(self):
        super().__init__("主题", "名称")


class AIServiceError(AppException):
    """AI 服务错误"""

    def __init__(self, message: str):
        super().__init__(message, code="AI_ERROR")


class ValidationError(AppException):
    """验证错误"""

    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")