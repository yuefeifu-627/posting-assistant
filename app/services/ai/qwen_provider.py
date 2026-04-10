"""通义千问 API 提供者"""

from app.services.ai.plugin import AIProvider, ProviderMetadata
from app.exceptions import AIServiceError
from app.logger import get_logger

logger = get_logger("qwen_provider")

QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


class QwenProvider(AIProvider):
    """通义千问 API 实现"""

    # 插件元数据
    metadata = ProviderMetadata(
        name="通义千问",
        type="qwen",
        version="1.0.0",
        description="阿里云的通义千问 API",
        requires_api_key=True,
        supports_stream=True,
        default_model="qwen-plus",
        configurable_params={
            "api_key": {"type": "string", "required": True, "description": "API 密钥"},
            "model": {"type": "string", "required": False, "default": "qwen-plus", "description": "模型名称"},
        }
    )

    def generate(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> str:
        api_key = self._config.get("api_key")
        if not api_key:
            raise AIServiceError("未配置 QWEN_API_KEY，请在.env文件中设置")

        model = self._config.get("model", self.metadata.default_model)

        try:
            import openai

            client = openai.OpenAI(api_key=api_key, base_url=QWEN_BASE_URL)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            logger.info(f"Qwen API 生成完成 (模型: {model})")
            return response.choices[0].message.content
        except ImportError:
            raise AIServiceError("请安装 openai 库: pip install openai")
        except Exception as e:
            logger.error(f"Qwen API 调用失败: {str(e)}")
            raise AIServiceError(f"Qwen API调用失败: {str(e)}")

    def test_connection(self) -> bool:
        return bool(self._config.get("api_key"))
