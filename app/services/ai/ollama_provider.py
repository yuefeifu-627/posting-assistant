"""Ollama 本地模型提供者"""

from typing import List

from app.services.ai.plugin import AIProvider, ProviderMetadata
from app.exceptions import AIServiceError
from app.logger import get_logger

logger = get_logger("ollama_provider")


class OllamaProvider(AIProvider):
    """Ollama 本地模型实现"""

    # 插件元数据
    metadata = ProviderMetadata(
        name="Ollama",
        type="ollama",
        version="1.0.0",
        description="本地 Ollama 模型服务",
        requires_api_key=False,
        supports_stream=True,
        default_model="qwen2.5",
        configurable_params={
            "base_url": {"type": "string", "required": False, "default": "http://localhost:11434", "description": "Ollama 服务地址"},
            "model": {"type": "string", "required": False, "default": "qwen2.5", "description": "模型名称"},
        }
    )

    def generate(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> str:
        base_url = self._config.get("base_url", "http://localhost:11434")
        model = self._config.get("model", self.metadata.default_model)

        try:
            import ollama

            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )
            logger.info(f"Ollama 生成完成 (模型: {model})")
            return response["message"]["content"]
        except ImportError:
            raise AIServiceError("请安装 ollama 库: pip install ollama")
        except Exception as e:
            logger.error(f"Ollama 生成失败: {str(e)}")
            raise AIServiceError(f"本地模型生成失败: {str(e)}")

    def test_connection(self) -> bool:
        try:
            import ollama
            ollama.list()
            return True
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        try:
            import ollama
            models = ollama.list()
            return [model["model"] for model in models.get("models", [])]
        except Exception:
            return []
