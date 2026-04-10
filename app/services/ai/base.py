"""AI 提供者抽象基类（向后兼容）"""

# 为了保持向后兼容，从 plugin 导入
from app.services.ai.plugin import AIProvider, ProviderMetadata

# 重新导出以保持兼容性
__all__ = ["AIProvider", "ProviderMetadata"]
