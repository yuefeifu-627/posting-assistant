"""AI 提供者模块 - 基于插件架构"""

# 为了向后兼容，保留工厂函数
from app.config import Settings
from app.services.ai.base import AIProvider, ProviderMetadata
from app.services.ai.plugin_manager import get_plugin_manager
from app.services.ai.ollama_provider import OllamaProvider
from app.services.ai.glm_provider import GLMProvider
from app.services.ai.qwen_provider import QwenProvider


def create_provider(provider_type: str, settings: Settings) -> AIProvider:
    """
    根据类型创建 AI 提供者（向后兼容的工厂函数）

    Args:
        provider_type: 提供者类型
        settings: 配置对象

    Returns:
        AI Provider 实例

    Raises:
        ValueError: 如果未知的提供者类型
    """
    manager = get_plugin_manager()

    # 确保插件已注册
    if not manager.get_provider_class("ollama"):
        manager.register(OllamaProvider)
    if not manager.get_provider_class("glm"):
        manager.register(GLMProvider)
    if not manager.get_provider_class("qwen"):
        manager.register(QwenProvider)

    # 根据类型创建实例
    if provider_type == "ollama":
        return manager.get_provider_instance(
            "ollama",
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        )
    elif provider_type == "glm":
        return manager.get_provider_instance(
            "glm",
            api_key=settings.glm_api_key,
            model=settings.glm_model,
            base_url=settings.glm_base_url,
        )
    elif provider_type == "qwen":
        return manager.get_provider_instance(
            "qwen",
            api_key=settings.qwen_api_key,
            model=settings.qwen_model,
        )
    else:
        raise ValueError(f"未知的 AI 提供者类型: {provider_type}")


__all__ = [
    "AIProvider",
    "ProviderMetadata",
    "create_provider",
    "get_plugin_manager",
    "OllamaProvider",
    "GLMProvider",
    "QwenProvider",
]
