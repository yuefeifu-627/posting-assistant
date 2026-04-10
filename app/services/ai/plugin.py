"""AI Provider 插件系统"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Type, Any
from dataclasses import dataclass, field


@dataclass
class ProviderMetadata:
    """Provider 元数据"""
    name: str
    type: str
    version: str = "1.0.0"
    description: str = ""
    requires_api_key: bool = False
    supports_stream: bool = False
    default_model: Optional[str] = None
    configurable_params: Dict[str, Any] = field(default_factory=dict)


class AIProvider(ABC):
    """AI 提供者基类，所有 AI 实现必须继承此类"""

    # 子类必须提供元数据
    metadata: ProviderMetadata = None

    def __init__(self, **config):
        """
        初始化 Provider

        Args:
            **config: 配置参数
        """
        self._config = config

    @abstractmethod
    def generate(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> str:
        """生成文本"""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """测试连接是否正常"""
        pass

    def get_name(self) -> str:
        """获取提供者名称"""
        return self.metadata.name if self.metadata else self.__class__.__name__

    def get_type(self) -> str:
        """获取提供者类型"""
        return self.metadata.type if self.metadata else "unknown"

    def get_metadata(self) -> ProviderMetadata:
        """获取元数据"""
        if self.metadata is None:
            return ProviderMetadata(name=self.get_name(), type="unknown")
        return self.metadata

    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self._config.copy()

    def is_configured(self) -> bool:
        """检查是否已正确配置"""
        if self.metadata.requires_api_key:
            return bool(self._config.get("api_key"))
        return True

    def validate_config(self) -> bool:
        """验证配置是否有效"""
        return self.is_configured()
