"""依赖注入容器测试"""

import pytest
from app.di import (
    DIContainer,
    IAIService,
    IThemeService,
    IPostService,
    ICorpusService,
    get_container,
    reset_container,
)
from app.services.ai_service import AIService
from app.services.ai.plugin_manager import reset_plugin_manager


class MockService:
    """模拟服务"""
    def __init__(self, value: str = "default"):
        self.value = value


class MockDependentService:
    """依赖其他服务的模拟服务"""
    def __init__(self, dependency: MockService):
        self.dependency = dependency


class TestDIContainer:
    """DI 容器测试"""

    def setup_method(self):
        """每个测试前重置容器和插件管理器"""
        reset_container()
        reset_plugin_manager()

    def test_singleton_registration(self):
        """测试单例注册"""
        container = DIContainer()
        container.register_singleton(IAIService, AIService)

        # 多次解析应该返回相同实例
        instance1 = container.resolve(IAIService)
        instance2 = container.resolve(IAIService)

        assert instance1 is instance2
        assert isinstance(instance1, IAIService)
        assert isinstance(instance1, AIService)

    def test_transient_registration(self):
        """测试瞬态注册"""
        container = DIContainer()
        container.register_transient(MockService, MockService)

        # 每次解析应该返回新实例
        instance1 = container.resolve(MockService)
        instance2 = container.resolve(MockService)

        assert instance1 is not instance2
        assert isinstance(instance1, MockService)

    def test_factory_registration(self):
        """测试工厂函数注册"""
        container = DIContainer()

        counter = [0]

        def factory(**kwargs):
            counter[0] += 1
            # 如果有 value 参数，使用它
            if 'value' in kwargs:
                return MockService(value=kwargs['value'])
            return MockService(value=f"instance-{counter[0]}")

        container.register_factory(MockService, factory)

        instance1 = container.resolve(MockService)
        instance2 = container.resolve(MockService)

        assert instance1.value == "instance-1"
        assert instance2.value == "instance-2"

    def test_auto_dependency_injection(self):
        """测试自动依赖注入"""
        container = DIContainer()
        container.register_transient(MockService, MockService)
        container.register_transient(MockDependentService, MockDependentService)

        dependent = container.resolve(MockDependentService)

        assert isinstance(dependent, MockDependentService)
        assert isinstance(dependent.dependency, MockService)

    def test_resolve_with_args(self):
        """测试带参数的解析"""
        container = DIContainer()
        container.register_transient(MockService, MockService)

        instance = container.resolve(MockService, value="custom")
        assert instance.value == "custom"

    def test_resolve_unregistered_service(self):
        """测试解析未注册的服务"""
        container = DIContainer()

        # 创建一个不注册默认服务的容器
        class EmptyContainer(DIContainer):
            def _register_defaults(self):
                pass  # 不注册任何默认服务

        fresh_container = EmptyContainer()
        with pytest.raises(ValueError, match="未注册"):
            fresh_container.resolve(IAIService)

    def test_unregister(self):
        """测试注销服务"""
        container = DIContainer()
        container.register_singleton(IAIService, AIService)

        # 注册后可以解析
        assert container.resolve(IAIService) is not None

        # 注销后不能解析
        container.unregister(IAIService)
        with pytest.raises(ValueError, match="未注册"):
            container.resolve(IAIService)

    def test_global_container(self):
        """测试全局容器"""
        reset_container()
        container1 = get_container()
        container2 = get_container()

        assert container1 is container2
        assert isinstance(container1, DIContainer)


class TestServiceInterfaces:
    """服务接口测试"""

    def setup_method(self):
        """每个测试前重置容器和插件管理器"""
        reset_container()
        reset_plugin_manager()

    def test_ai_service_interface(self):
        """测试 AI 服务接口"""
        container = DIContainer()
        service = container.resolve(IAIService)

        assert isinstance(service, IAIService)
        assert hasattr(service, 'generate_post')
        assert hasattr(service, 'analyze_writing_style')
        assert hasattr(service, 'test_connection')
