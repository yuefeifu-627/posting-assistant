"""依赖注入容器实现"""

from typing import Type, TypeVar, Callable, Any, Dict, Optional
from functools import lru_cache
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import get_settings
from app.di.interfaces import (
    IThemeRepository,
    IPostRepository,
    ICorpusRepository,
    IThemeService,
    IPostService,
    ICorpusService,
    IAIService,
)
from app.repositories.theme_repo import ThemeRepository
from app.repositories.post_repo import PostRepository
from app.repositories.corpus_repo import CorpusRepository
from app.services.theme_service import ThemeService
from app.services.post_service import PostService
from app.services.corpus_service import CorpusService
from app.services.ai_service import AIService

T = TypeVar('T')


class DIContainer:
    """
    简单的依赖注入容器

    支持单例和瞬态生命周期，支持构造函数注入
    """

    _instance: Optional['DIContainer'] = None
    _services: Dict[Type, Any] = {}
    _factories: Dict[Type, Callable] = {}
    _singletons: Dict[Type, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._services = {}
        self._factories = {}
        self._singletons = {}
        self._register_defaults()

    def _register_defaults(self):
        """注册默认服务"""
        # 单例服务
        self.register_singleton(IAIService, AIService)

        # 工厂函数（每次创建新实例）
        self.register_factory(IThemeRepository, lambda: ThemeRepository(next(get_db())))
        self.register_factory(IPostRepository, lambda: PostRepository(next(get_db())))
        self.register_factory(ICorpusRepository, lambda: CorpusRepository(next(get_db())))

        # 服务（需要数据库会话）
        self.register_factory(
            IThemeService,
            lambda db: ThemeService(db)
        )
        self.register_factory(
            IPostService,
            lambda db: PostService(db, self.resolve(IAIService))
        )
        self.register_factory(
            ICorpusService,
            lambda db: CorpusService(db, self.resolve(IAIService))
        )

    def register_singleton(self, interface: Type[T], implementation: Type[T] or T):
        """
        注册单例服务

        Args:
            interface: 接口类型
            implementation: 实现类型或实例
        """
        if isinstance(implementation, type):
            # 存储类类型，标记为单例
            self._services[interface] = (implementation, "singleton")
        else:
            # 直接存储实例
            self._singletons[interface] = implementation

    def register_factory(self, interface: Type[T], factory: Callable):
        """
        注册工厂函数

        Args:
            interface: 接口类型
            factory: 工厂函数
        """
        self._factories[interface] = factory

    def register_transient(self, interface: Type[T], implementation: Type[T]):
        """
        注册瞬态服务（每次都创建新实例）

        Args:
            interface: 接口类型
            implementation: 实现类型
        """
        self._services[interface] = implementation

    def unregister(self, interface: Type[T]):
        """
        注销服务

        Args:
            interface: 接口类型
        """
        if interface in self._services:
            del self._services[interface]
        if interface in self._factories:
            del self._factories[interface]
        if interface in self._singletons:
            del self._singletons[interface]

    def resolve(self, interface: Type[T], *args, **kwargs) -> T:
        """
        解析服务

        Args:
            interface: 接口类型
            *args: 构造函数参数
            **kwargs: 构造函数关键字参数

        Returns:
            服务实例

        Raises:
            ValueError: 如果服务未注册
        """
        # 检查单例缓存
        if interface in self._singletons:
            return self._singletons[interface]

        # 检查工厂函数
        if interface in self._factories:
            factory = self._factories[interface]
            # 传递所有参数给工厂函数
            instance = factory(*args, **kwargs)
            return instance

        # 检查服务类型
        if interface in self._services:
            implementation = self._services[interface]

            # 检查是否是单例类（元组形式）
            if isinstance(implementation, tuple) and len(implementation) == 2 and implementation[1] == "singleton":
                cls = implementation[0]
                # 检查是否已创建实例
                if interface in self._singletons:
                    return self._singletons[interface]
                # 创建新实例并缓存
                instance = self._create_instance(cls, *args, **kwargs)
                self._singletons[interface] = instance
                return instance

            if isinstance(implementation, type):
                # 如果是类，尝试自动注入依赖
                return self._create_instance(implementation, *args, **kwargs)
            return implementation

        raise ValueError(f"服务 {interface.__name__} 未注册到容器中")

    def _create_instance(self, cls: Type[T], *args, **kwargs) -> T:
        """
        创建实例，尝试自动注入依赖

        Args:
            cls: 类类型
            *args: 构造函数参数
            **kwargs: 构造函数关键字参数

        Returns:
            实例
        """
        import inspect

        # 获取构造函数签名
        sig = inspect.signature(cls.__init__)
        parameters = sig.parameters

        # 构造参数字典
        resolved_args = {}
        for name, param in parameters.items():
            if name == 'self':
                continue

            # 如果参数已提供，使用提供的值
            if name in kwargs:
                resolved_args[name] = kwargs[name]
                continue

            # 尝试从容器解析
            if param.annotation != inspect.Parameter.empty:
                try:
                    resolved_args[name] = self.resolve(param.annotation)
                except ValueError:
                    # 无法解析，使用默认值或跳过
                    if param.default != inspect.Parameter.empty:
                        resolved_args[name] = param.default

        # 创建实例
        return cls(*args, **resolved_args, **{k: v for k, v in kwargs.items() if k not in resolved_args})

    def clear(self):
        """清空容器（主要用于测试）"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._initialized = False


# 全局容器实例
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """获取全局容器实例"""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def reset_container():
    """重置容器（主要用于测试）"""
    global _container
    if _container is not None:
        _container.clear()
        _container = None
