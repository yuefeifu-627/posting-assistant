"""AI Provider 插件管理器"""

import importlib
import inspect
from typing import Dict, Type, List, Optional, Any
from pathlib import Path

from app.services.ai.plugin import AIProvider, ProviderMetadata
from app.config import get_settings
from app.logger import get_logger

logger = get_logger("plugin_manager")


class PluginManager:
    """
    AI Provider 插件管理器

    负责：
    - 插件注册和发现
    - 插件生命周期管理
    - 插件配置管理
    """

    def __init__(self):
        self._providers: Dict[str, Type[AIProvider]] = {}
        self._instances: Dict[str, AIProvider] = {}
        self._metadata: Dict[str, ProviderMetadata] = {}
        self._initialized = False

    def register(self, provider_class: Type[AIProvider], override: bool = False):
        """
        注册一个 Provider 插件

        Args:
            provider_class: Provider 类
            override: 是否覆盖已存在的注册

        Raises:
            ValueError: 如果 Provider 类型已存在且不允许覆盖
        """
        if not issubclass(provider_class, AIProvider):
            raise ValueError(f"{provider_class.__name__} 必须继承自 AIProvider")

        # 获取元数据
        metadata = provider_class.metadata
        if metadata is None:
            logger.warning(f"{provider_class.__name__} 没有定义 metadata，使用默认值")
            metadata = ProviderMetadata(
                name=provider_class.__name__,
                type=provider_class.__name__.lower().replace("provider", "")
            )
            provider_class.metadata = metadata

        provider_type = metadata.type

        # 检查是否已注册
        if provider_type in self._providers and not override:
            raise ValueError(f"Provider 类型 '{provider_type}' 已注册，使用 override=True 覆盖")

        self._providers[provider_type] = provider_class
        self._metadata[provider_type] = metadata
        logger.info(f"注册 Provider: {metadata.name} (类型: {provider_type})")

    def unregister(self, provider_type: str):
        """
        注销一个 Provider 插件

        Args:
            provider_type: Provider 类型
        """
        if provider_type in self._providers:
            provider_name = self._metadata[provider_type].name
            del self._providers[provider_type]
            del self._metadata[provider_type]
            if provider_type in self._instances:
                del self._instances[provider_type]
            logger.info(f"注销 Provider: {provider_name}")

    def get_provider_class(self, provider_type: str) -> Optional[Type[AIProvider]]:
        """
        获取 Provider 类

        Args:
            provider_type: Provider 类型

        Returns:
            Provider 类，如果不存在返回 None
        """
        return self._providers.get(provider_type)

    def get_provider_instance(self, provider_type: str, **config) -> Optional[AIProvider]:
        """
        获取 Provider 实例（单例模式）

        Args:
            provider_type: Provider 类型
            **config: 配置参数

        Returns:
            Provider 实例，如果不存在返回 None
        """
        # 检查缓存
        if provider_type in self._instances:
            return self._instances[provider_type]

        # 创建新实例
        provider_class = self.get_provider_class(provider_type)
        if provider_class is None:
            return None

        try:
            instance = provider_class(**config)
            self._instances[provider_type] = instance
            logger.info(f"创建 Provider 实例: {instance.get_name()}")
            return instance
        except Exception as e:
            logger.error(f"创建 Provider 实例失败 ({provider_type}): {str(e)}")
            return None

    def list_providers(self) -> List[ProviderMetadata]:
        """
        列出所有已注册的 Provider

        Returns:
            Provider 元数据列表
        """
        return list(self._metadata.values())

    def get_metadata(self, provider_type: str) -> Optional[ProviderMetadata]:
        """
        获取 Provider 元数据

        Args:
            provider_type: Provider 类型

        Returns:
            Provider 元数据，如果不存在返回 None
        """
        return self._metadata.get(provider_type)

    def initialize_from_config(self, settings: Any):
        """
        根据配置初始化可用的 Provider

        Args:
            settings: 配置对象
        """
        self._initialized = True

        # 初始化 Ollama（总是可用）
        if "ollama" in self._providers:
            self.get_provider_instance(
                "ollama",
                base_url=getattr(settings, "ollama_base_url", "http://localhost:11434"),
                model=getattr(settings, "ollama_model", "qwen3.5:9b"),
            )

        # 初始化 GLM（如果有 API Key）
        if hasattr(settings, "glm_api_key") and settings.glm_api_key and "glm" in self._providers:
            self.get_provider_instance(
                "glm",
                api_key=settings.glm_api_key,
                model=getattr(settings, "glm_model", "glm-4v"),
                base_url=getattr(settings, "glm_base_url", "https://open.bigmodel.cn/api/paas/v4"),
            )

        # 初始化 MiniMax（如果有 API Key）
        if hasattr(settings, "minmax_api_key") and settings.minmax_api_key and "minmax" in self._providers:
            self.get_provider_instance(
                "minmax",
                api_key=settings.minmax_api_key,
                model=getattr(settings, "minmax_model", "MinMax-Text-01"),
                base_url=getattr(settings, "minmax_base_url", "https://api.minimax.chat/v1"),
            )

        logger.info(f"已初始化 {len(self._instances)} 个 Provider 实例")

    def get_configured_providers(self) -> List[str]:
        """
        获取已配置且可用的 Provider 类型列表

        Returns:
            Provider 类型列表
        """
        return [
            provider_type
            for provider_type, instance in self._instances.items()
            if instance.test_connection()
        ]

    def get_best_provider(self, preferred_types: Optional[List[str]] = None) -> Optional[AIProvider]:
        """
        获取最佳可用的 Provider

        Args:
            preferred_types: 优先级类型列表，按优先级排序

        Returns:
            最佳可用的 Provider 实例
        """
        # 使用优先级列表
        if preferred_types:
            for provider_type in preferred_types:
                instance = self._instances.get(provider_type)
                if instance and instance.test_connection():
                    return instance

        # 返回第一个可用的
        for instance in self._instances.values():
            if instance.test_connection():
                return instance

        return None

    def discover_plugins(self, plugin_dir: Optional[str] = None):
        """
        自动发现插件

        Args:
            plugin_dir: 插件目录路径，如果为 None 则使用默认目录
        """
        if plugin_dir is None:
            plugin_dir = Path(__file__).parent / "plugins"

        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            logger.info(f"插件目录不存在: {plugin_path}")
            return

        logger.info(f"开始发现插件: {plugin_path}")

        # 遍历插件目录
        for py_file in plugin_path.glob("*_provider.py"):
            module_name = py_file.stem
            try:
                # 动态导入模块
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 查找 Provider 类
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and
                            issubclass(obj, AIProvider) and
                            obj is not AIProvider):
                        self.register(obj)
                        logger.info(f"自动发现插件: {name}")

            except Exception as e:
                logger.warning(f"加载插件失败 ({py_file}): {str(e)}")


# 全局插件管理器实例
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """获取全局插件管理器实例"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def reset_plugin_manager():
    """重置插件管理器（主要用于测试）"""
    global _plugin_manager
    _plugin_manager = None
