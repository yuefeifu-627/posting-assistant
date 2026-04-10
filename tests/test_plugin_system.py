"""插件系统测试"""

import pytest
from app.services.ai.plugin import AIProvider, ProviderMetadata
from app.services.ai.plugin_manager import (
    PluginManager,
    get_plugin_manager,
    reset_plugin_manager,
)
from app.services.ai.ollama_provider import OllamaProvider
from app.services.ai.glm_provider import GLMProvider
from app.services.ai.qwen_provider import QwenProvider


class MockProvider(AIProvider):
    """模拟 Provider"""
    metadata = ProviderMetadata(
        name="Mock Provider",
        type="mock",
        version="1.0.0",
        description="A mock provider for testing",
    )

    def generate(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> str:
        return f"Generated: {prompt[:50]}..."

    def test_connection(self) -> bool:
        return True


class TestPluginManager:
    """插件管理器测试"""

    def setup_method(self):
        """每个测试前重置插件管理器"""
        reset_plugin_manager()

    def test_register_provider(self):
        """测试注册 Provider"""
        manager = get_plugin_manager()
        manager.register(MockProvider)

        assert manager.get_provider_class("mock") is MockProvider
        assert manager.get_metadata("mock") is not None
        assert manager.get_metadata("mock").name == "Mock Provider"

    def test_register_duplicate_provider(self):
        """测试注册重复 Provider"""
        manager = get_plugin_manager()
        manager.register(MockProvider)

        # 不允许覆盖应该抛出异常
        with pytest.raises(ValueError, match="已注册"):
            manager.register(MockProvider, override=False)

        # 允许覆盖应该成功
        manager.register(MockProvider, override=True)

    def test_unregister_provider(self):
        """测试注销 Provider"""
        manager = get_plugin_manager()
        manager.register(MockProvider)

        assert manager.get_provider_class("mock") is MockProvider

        manager.unregister("mock")

        assert manager.get_provider_class("mock") is None
        assert manager.get_metadata("mock") is None

    def test_list_providers(self):
        """测试列出所有 Provider"""
        manager = get_plugin_manager()
        manager.register(MockProvider)
        manager.register(OllamaProvider)

        providers = manager.list_providers()

        assert len(providers) >= 2
        provider_types = [p.type for p in providers]
        assert "mock" in provider_types
        assert "ollama" in provider_types

    def test_get_provider_instance(self):
        """测试获取 Provider 实例"""
        manager = get_plugin_manager()
        manager.register(MockProvider)

        instance1 = manager.get_provider_instance("mock")
        instance2 = manager.get_provider_instance("mock")

        # 应该返回相同的实例（单例）
        assert instance1 is instance2
        assert isinstance(instance1, MockProvider)
        assert isinstance(instance1, AIProvider)

    def test_get_provider_instance_with_config(self):
        """测试带配置获取 Provider 实例"""
        manager = get_plugin_manager()
        manager.register(MockProvider)

        instance = manager.get_provider_instance("mock", custom_param="value")

        assert isinstance(instance, MockProvider)
        assert instance.get_config()["custom_param"] == "value"

    def test_get_best_provider(self):
        """测试获取最佳 Provider"""
        manager = get_plugin_manager()
        manager.register(MockProvider)

        # 创建一个连接失败的 Provider
        class FailingProvider(AIProvider):
            metadata = ProviderMetadata(
                name="Failing Provider",
                type="failing",
            )

            def generate(self, prompt, temperature, max_tokens, **kwargs) -> str:
                return "test"

            def test_connection(self) -> bool:
                return False

        manager.register(FailingProvider)

        # 获取最佳 Provider（应该返回可用的）
        best = manager.get_best_provider(["failing", "mock"])

        assert best is not None
        assert isinstance(best, MockProvider)

    def test_get_configured_providers(self):
        """测试获取已配置的 Provider"""
        manager = get_plugin_manager()
        manager.register(MockProvider)

        # 初始化实例
        manager.get_provider_instance("mock")

        configured = manager.get_configured_providers()

        assert "mock" in configured

    def test_global_plugin_manager(self):
        """测试全局插件管理器"""
        reset_plugin_manager()
        manager1 = get_plugin_manager()
        manager2 = get_plugin_manager()

        assert manager1 is manager2
        assert isinstance(manager1, PluginManager)


class TestProviderMetadata:
    """Provider 元数据测试"""

    def test_provider_get_metadata(self):
        """测试获取 Provider 元数据"""
        provider = MockProvider()
        metadata = provider.get_metadata()

        assert metadata.name == "Mock Provider"
        assert metadata.type == "mock"
        assert metadata.version == "1.0.0"

    def test_provider_get_name(self):
        """测试获取 Provider 名称"""
        provider = MockProvider()
        assert provider.get_name() == "Mock Provider"

    def test_provider_get_type(self):
        """测试获取 Provider 类型"""
        provider = MockProvider()
        assert provider.get_type() == "mock"

    def test_provider_is_configured(self):
        """测试 Provider 配置状态"""
        # 不需要 API Key 的 Provider
        provider = MockProvider()
        assert provider.is_configured() is True

        # 需要 API Key 的 Provider
        glm = GLMProvider(api_key="")
        assert glm.is_configured() is False

        glm_with_key = GLMProvider(api_key="test-key")
        assert glm_with_key.is_configured() is True


class TestBuiltinProviders:
    """内置 Provider 测试"""

    def test_ollama_provider_metadata(self):
        """测试 Ollama Provider 元数据"""
        assert OllamaProvider.metadata is not None
        assert OllamaProvider.metadata.type == "ollama"
        assert OllamaProvider.metadata.requires_api_key is False

    def test_glm_provider_metadata(self):
        """测试 GLM Provider 元数据"""
        assert GLMProvider.metadata is not None
        assert GLMProvider.metadata.type == "glm"
        assert GLMProvider.metadata.requires_api_key is True

    def test_qwen_provider_metadata(self):
        """测试 Qwen Provider 元数据"""
        assert QwenProvider.metadata is not None
        assert QwenProvider.metadata.type == "qwen"
        assert QwenProvider.metadata.requires_api_key is True

    def test_ollama_provider_without_ollama(self):
        """测试没有安装 ollama 库时的行为"""
        provider = OllamaProvider(base_url="http://localhost:11434", model="test")

        # test_connection 应该返回 False（如果没有 ollama）
        result = provider.test_connection()
        assert isinstance(result, bool)

    def test_glm_provider_generate_without_key(self):
        """测试没有 API Key 时 GLM Provider 的行为"""
        provider = GLMProvider(api_key="", model="glm-4v", base_url="https://test.com")

        with pytest.raises(Exception):  # AIServiceError
            provider.generate("test", 0.7, 100)

    def test_provider_configurable_params(self):
        """测试 Provider 可配置参数"""
        assert OllamaProvider.metadata.configurable_params is not None
        assert "base_url" in OllamaProvider.metadata.configurable_params
        assert "model" in OllamaProvider.metadata.configurable_params
