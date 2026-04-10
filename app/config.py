from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = "用车总结生成器"
    debug: bool = False

    # 数据库
    database_url: str = ""

    # Ollama 配置
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5:9b"

    # 通义千问 API
    qwen_api_key: str = ""
    qwen_model: str = "qwen-plus"

    # GLM API
    glm_api_key: str = ""
    glm_model: str = "glm-4v"
    glm_base_url: str = "https://open.bigmodel.cn/api/paas/v4"

    # AI 参数
    ai_temperature: float = 0.7
    ai_max_tokens: int = 4096

    # 车辆信息
    vehicle_model: str = "2025款极氪001 WE95版本"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果没有配置 database_url，使用默认路径
        if not self.database_url:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(project_root, "data")
            os.makedirs(data_dir, exist_ok=True)
            db_file = os.path.join(data_dir, "posts.db")
            self.database_url = f"sqlite:///{db_file}"


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例）"""
    return Settings()