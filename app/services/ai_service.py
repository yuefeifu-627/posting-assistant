"""AI 服务 - 文章生成和风格分析（基于插件架构）"""

from typing import Optional, List, Dict

from app.config import get_settings
from app.exceptions import AIServiceError
from app.logger import get_logger
from app.services.ai.plugin_manager import get_plugin_manager
from app.interfaces import IAIService

logger = get_logger("ai_service")


class AIService(IAIService):
    """AI 服务类 - 基于插件架构"""

    def __init__(self):
        settings = get_settings()
        self.temperature = settings.ai_temperature
        self.max_tokens = settings.ai_max_tokens
        self.vehicle_model = settings.vehicle_model

        # 获取插件管理器
        self.plugin_manager = get_plugin_manager()

        # 注册内置插件
        self._register_builtin_plugins()

        # 从配置初始化
        self.plugin_manager.initialize_from_config(settings)

    def _register_builtin_plugins(self):
        """注册内置插件"""
        from app.services.ai.ollama_provider import OllamaProvider
        from app.services.ai.glm_provider import GLMProvider
        from app.services.ai.qwen_provider import QwenProvider

        # 使用 override=True 避免重复注册错误
        self.plugin_manager.register(OllamaProvider, override=True)
        self.plugin_manager.register(GLMProvider, override=True)
        self.plugin_manager.register(QwenProvider, override=True)

    def _get_provider(self, use_api: bool = False, api_type: str = "glm"):
        """
        获取 AI 提供者

        Args:
            use_api: 是否使用云端 API
            api_type: API 类型 (glm/qwen)

        Returns:
            AI Provider 实例

        Raises:
            AIServiceError: 如果无法获取可用的 Provider
        """
        if use_api:
            provider = self.plugin_manager.get_provider_instance(api_type)
            if provider is None:
                raise AIServiceError(f"未配置 {api_type.upper()} API Key，请在.env文件中设置")
            return provider

        # 默认使用 Ollama
        provider = self.plugin_manager.get_provider_instance("ollama")
        if provider is None:
            raise AIServiceError("Ollama Provider 未注册")
        return provider

    def generate_post(
        self,
        theme: str,
        summary: str,
        requirements: Optional[str] = None,
        post_length: int = 500,
        use_api: bool = False,
        api_type: str = "glm",
        style_profile: Optional[str] = None,
    ) -> str:
        """
        根据提要润色生成帖子

        Args:
            theme: 文章主题
            summary: 用户提供的提要/大纲
            requirements: 主办方的任务要求
            post_length: 发帖字数限制
            use_api: 是否使用云端API
            api_type: 云端API类型 (glm/qwen)
            style_profile: 风格特征描述
        """
        prompt = self._build_generation_prompt(theme, summary, requirements, post_length, style_profile)
        provider = self._get_provider(use_api, api_type)

        logger.info(f"生成帖子: 主题={theme}, 字数={post_length}, 提供者={provider.get_name()}")
        return provider.generate(prompt, self.temperature, self.max_tokens)

    def analyze_writing_style(self, posts: List[str]) -> str:
        """分析用户历史帖子的写作风格"""
        prompt = self._build_style_analysis_prompt(posts)

        logger.info(f"分析写作风格: {len(posts)}篇帖子")

        # 优先级：GLM > Qwen > Ollama
        provider = self.plugin_manager.get_best_provider(["glm", "qwen", "ollama"])

        if provider is None:
            logger.error("没有可用的 AI 提供者")
            return "语气自然随性，像朋友聊天；句子长短不一，表达真实直接；偶尔会吐槽感叹，不过分修饰。"

        try:
            result = provider.generate(prompt, temperature=0.3, max_tokens=500)
            logger.info(f"风格分析完成 ({provider.get_name()})")
            return result
        except Exception as e:
            logger.error(f"风格分析失败 ({provider.get_name()}): {str(e)}")
            # 返回默认风格
            return "语气自然随性，像朋友聊天；句子长短不一，表达真实直接；偶尔会吐槽感叹，不过分修饰。"

    def test_connection(self) -> bool:
        """测试 Ollama 连接是否正常"""
        try:
            provider = self.plugin_manager.get_provider_instance("ollama")
            return provider is not None and provider.test_connection()
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        """获取可用的本地模型列表"""
        try:
            from app.services.ai.ollama_provider import OllamaProvider

            provider = self.plugin_manager.get_provider_instance("ollama")
            if isinstance(provider, OllamaProvider):
                return provider.get_available_models()
        except Exception:
            pass
        return []

    def check_api_config(self) -> dict:
        """检查 API 配置状态"""
        s = get_settings()
        if s.glm_api_key:
            return {"api_key_configured": True, "api_model": s.glm_model}
        elif s.qwen_api_key:
            return {"api_key_configured": True, "api_model": s.qwen_model}
        else:
            return {"api_key_configured": False, "api_model": None}

    def get_provider_info(self) -> Dict[str, dict]:
        """获取所有 provider 的状态信息"""
        info = {}
        for provider_type in self.plugin_manager.list_providers():
            instance = self.plugin_manager.get_provider_instance(provider_type.type)
            if instance:
                info[provider_type.type] = {
                    "name": instance.get_name(),
                    "type": instance.get_type(),
                    "available": instance.test_connection(),
                    "metadata": instance.get_metadata().__dict__,
                }
        return info

    def get_plugin_metadata(self) -> List[Dict]:
        """获取所有插件的元数据"""
        return [md.__dict__ for md in self.plugin_manager.list_providers()]

    # === Prompt 构建方法 ===

    def _build_generation_prompt(
        self,
        theme: str,
        summary: str,
        requirements: Optional[str],
        post_length: int,
        style_profile: Optional[str],
    ) -> str:
        """构建帖子生成 prompt"""
        prompt = f"""你是一位热爱汽车的男性车主，有着多年的驾驶经验。你的车型是{self.vehicle_model}，主要用车场景是上下班通勤。

现在你要根据提供的提要，润色生成一篇用车分享帖子。

【帖子主题】
{theme}

【内容提要】
{summary}
"""
        if requirements:
            prompt += f"""
【主办方任务要求】
{requirements}
"""
        if style_profile:
            prompt += f"""
【你的写作风格特征】
{style_profile}

请严格按照上面的风格特征来写，保持你一贯的语气和表达习惯。
"""
        prompt += f"""
【写作要求】
1. 根据提要扩展成完整帖子，不要遗漏要点
2. 语言自然，像平时和朋友聊天一样
3. 千万不要写成"首先、其次、最后"的八股文
4. 避免"总的来说、综上所述"这类AI套话
5. 句子长短不一，有长有短
6. 字数控制在{post_length}字左右

请生成帖子内容："""
        return prompt

    def _build_style_analysis_prompt(self, posts: List[str]) -> str:
        """构建风格分析 prompt"""
        combined = "\n\n---\n\n".join(posts[:10])
        if len(combined) > 3000:
            combined = combined[:3000] + "..."

        return f"""请分析以下几篇车主帖子的写作风格，总结出作者的写作特征。

要求：
1. 分析作者的语气特点（比如：随性、正式、幽默、吐槽等）
2. 分析句式特点（比如：长短句搭配、是否喜欢用感叹号、问句使用等）
3. 分析常用表达习惯（比如：口头禅、常用词、开头结尾方式等）
4. 分析段落结构特点
5. 其他明显的个人风格

请用简洁的要点形式总结，每条1-2句话，总共不超过200字。

以下是作者的帖子：
---
{combined}
---

请输出风格特征总结："""
