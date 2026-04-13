"""服务接口定义 - 用于依赖注入"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from sqlalchemy.orm import Session


# === Repository 接口 ===

class IThemeRepository(ABC):
    """主题仓储接口"""

    @abstractmethod
    def get_by_id(self, id: int):
        """根据ID获取主题"""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100):
        """获取所有主题"""
        pass

    @abstractmethod
    def create(self, name: str, post_length: int):
        """创建主题"""
        pass

    @abstractmethod
    def update(self, theme, name: str = None, post_length: int = None):
        """更新主题"""
        pass

    @abstractmethod
    def delete(self, theme):
        """删除主题"""
        pass

    @abstractmethod
    def get_by_name(self, name: str):
        """根据名称获取主题"""
        pass

    @abstractmethod
    def count(self) -> int:
        """统计主题数量"""
        pass


class IPostRepository(ABC):
    """帖子仓储接口"""

    @abstractmethod
    def get_by_id(self, id: int):
        """根据ID获取帖子"""
        pass

    @abstractmethod
    def get_all(self, theme_id: int = None, skip: int = 0, limit: int = 20):
        """获取帖子列表"""
        pass

    @abstractmethod
    def create(self, theme_id: int, content: str, summary: str = None, requirements: str = None):
        """创建帖子"""
        pass

    @abstractmethod
    def update(self, post, content: str = None, summary: str = None, requirements: str = None):
        """更新帖子"""
        pass

    @abstractmethod
    def delete(self, post):
        """删除帖子"""
        pass

    @abstractmethod
    def get_theme(self, theme_id: int):
        """获取帖子关联的主题"""
        pass

    @abstractmethod
    def count(self, theme_id: int = None) -> int:
        """统计帖子数量"""
        pass

    @abstractmethod
    def get_by_theme(self, theme_id: int, skip: int = 0, limit: int = 20):
        """获取指定主题的帖子"""
        pass


class ICorpusRepository(ABC):
    """语料库仓储接口"""

    @abstractmethod
    def get_by_id(self, id: int):
        """根据ID获取用户帖子"""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100):
        """获取所有用户帖子"""
        pass

    @abstractmethod
    def create(self, title: str, content: str, tags: str = None, note: str = None):
        """创建用户帖子"""
        pass

    @abstractmethod
    def update(self, post, title: str = None, content: str = None, tags: str = None, note: str = None):
        """更新用户帖子"""
        pass

    @abstractmethod
    def delete(self, post):
        """删除用户帖子"""
        pass

    @abstractmethod
    def get_recent(self, limit: int = 10):
        """获取最近的帖子用于风格分析"""
        pass

    @abstractmethod
    def get_style_profile(self):
        """获取风格特征"""
        pass

    @abstractmethod
    def save_style_profile(self, content: str):
        """保存风格特征"""
        pass

    @abstractmethod
    def count(self) -> int:
        """统计帖子数量"""
        pass


# === Service 接口 ===

class IThemeService(ABC):
    """主题服务接口"""

    @abstractmethod
    def get_by_id(self, id: int) -> dict:
        """根据ID获取主题"""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> dict:
        """获取所有主题"""
        pass

    @abstractmethod
    def create(self, name: str, post_length: int = 500) -> dict:
        """创建主题"""
        pass

    @abstractmethod
    def update(self, id: int, name: str = None, post_length: int = None) -> dict:
        """更新主题"""
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        """删除主题"""
        pass


class IPostService(ABC):
    """帖子服务接口"""

    @abstractmethod
    def generate(self, theme_id: int, summary: str, requirements: str = None,
                 post_length: int = None, use_api: bool = False) -> dict:
        """生成帖子"""
        pass

    @abstractmethod
    def create(self, theme_id: int, content: str, summary: str = None, requirements: str = None) -> dict:
        """手动创建帖子"""
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> dict:
        """获取单个帖子"""
        pass

    @abstractmethod
    def get_all(self, theme_id: int = None, skip: int = 0, limit: int = 20) -> dict:
        """获取帖子列表"""
        pass

    @abstractmethod
    def update(self, id: int, content: str = None, summary: str = None, requirements: str = None) -> dict:
        """更新帖子"""
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        """删除帖子"""
        pass


class ICorpusService(ABC):
    """语料库服务接口"""

    @abstractmethod
    def get_by_id(self, id: int) -> dict:
        """根据ID获取用户帖子"""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> dict:
        """获取所有用户帖子"""
        pass

    @abstractmethod
    def create(self, title: str, content: str, tags: str = None, note: str = None) -> dict:
        """创建用户帖子"""
        pass

    @abstractmethod
    def update(self, id: int, title: str = None, content: str = None, tags: str = None, note: str = None) -> dict:
        """更新用户帖子"""
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        """删除用户帖子"""
        pass

    @abstractmethod
    def analyze_writing_style(self) -> str:
        """分析写作风格"""
        pass

    @abstractmethod
    def get_style_profile(self) -> Optional[str]:
        """获取当前风格特征"""
        pass


class IAIService(ABC):
    """AI服务接口"""

    @abstractmethod
    def generate_post(self, theme: str, summary: str, requirements: Optional[str] = None,
                      post_length: int = 500, use_api: bool = False, api_type: str = "glm",
                      style_profile: Optional[str] = None) -> str:
        """生成帖子内容"""
        pass

    @abstractmethod
    def analyze_writing_style(self, posts: List[str]) -> str:
        """分析写作风格"""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """测试连接"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass

    @abstractmethod
    def check_api_config(self) -> dict:
        """检查API配置"""
        pass

    @abstractmethod
    def get_provider_info(self) -> Dict[str, dict]:
        """获取提供者信息"""
        pass

    @abstractmethod
    def get_plugin_metadata(self) -> List[Dict]:
        """获取插件元数据"""
        pass
