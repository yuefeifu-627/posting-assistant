"""MiniMax API 提供者"""

from app.services.ai.plugin import AIProvider, ProviderMetadata
from app.exceptions import AIServiceError
from app.logger import get_logger

logger = get_logger("minmax_provider")

MINMAX_BASE_URL = "https://api.minimax.chat/v1"


class MiniMaxProvider(AIProvider):
    """MiniMax API 实现"""

    # 插件元数据
    metadata = ProviderMetadata(
        name="MiniMax",
        type="minmax",
        version="1.0.0",
        description="MiniMax 的 M2.7 模型 API",
        requires_api_key=True,
        supports_stream=True,
        default_model="MinMax-Text-01",
        configurable_params={
            "api_key": {"type": "string", "required": True, "description": "API 密钥"},
            "model": {"type": "string", "required": False, "default": "MinMax-Text-01", "description": "模型名称"},
            "base_url": {"type": "string", "required": False, "default": MINMAX_BASE_URL, "description": "API 基础 URL"},
        }
    )

    def generate(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> str:
        api_key = self._config.get("api_key")
        if not api_key:
            raise AIServiceError("未配置 MINMAX_API_KEY，请在.env文件中设置")

        model = self._config.get("model", self.metadata.default_model)
        base_url = self._config.get("base_url", MINMAX_BASE_URL)

        try:
            import openai

            client = openai.OpenAI(api_key=api_key, base_url=base_url)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            logger.info(f"MiniMax API 生成完成 (模型: {model})")
            return response.choices[0].message.content
        except ImportError:
            raise AIServiceError("请安装 openai 库: pip install openai")
        except Exception as e:
            logger.error(f"MiniMax API 调用失败: {str(e)}")
            raise AIServiceError(f"MiniMax API调用失败: {str(e)}")

    def test_connection(self) -> bool:
        return bool(self._config.get("api_key"))