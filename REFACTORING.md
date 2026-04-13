# 项目重构文档

## 概述

本次重构主要完成了三个核心目标：

1. **增强输入验证** - 添加了全面的输入验证和安全防护
2. **实现依赖注入** - 引入了 DI 容器和服务接口抽象
3. **AI 服务插件化** - 重构 AI 服务为插件化架构

---

## 1. 增强输入验证

### 新增模块

#### `app/validators/`
验证器模块，包含：

- **`string_validator.py`** - 字符串验证和清理工具
  - `sanitize_html()` - HTML 转义，防止 XSS 攻击
  - `sanitize_sql_input()` - SQL 注入防护
  - `detect_xss()` - XSS 攻击检测
  - `detect_sql_injection()` - SQL 注入检测
  - `clean_whitespace()` - 空白字符清理
  - `validate_text_content()` - 通用文本验证
  - `validate_list_items()` - 列表验证

- **`business_validators.py`** - 业务规则验证
  - `validate_theme_name()` - 主题名称验证
  - `validate_post_content()` - 帖子内容验证
  - `validate_summary()` - 提要验证
  - `validate_requirements()` - 任务要求验证
  - `validate_post_length()` - 字数限制验证
  - `validate_ai_temperature()` - AI 温度参数验证
  - `validate_max_tokens()` - 最大 token 验证

### 集成方式

在 `app/schemas.py` 中通过 Pydantic 的 `@field_validator` 集成验证器：

```python
class ThemeCreate(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_theme_name(v)
```

---

## 2. 依赖注入 (DI)

### 新增模块

#### `app/di/`
依赖注入模块，包含：

- **`interfaces.py`** - 服务接口定义
  - `IThemeRepository` - 主题仓储接口
  - `IPostRepository` - 帖子仓储接口
  - `ICorpusRepository` - 语料库仓储接口
  - `IThemeService` - 主题服务接口
  - `IPostService` - 帖子服务接口
  - `ICorpusService` - 语料库服务接口
  - `IAIService` - AI 服务接口

- **`container.py`** - DI 容器实现
  - 支持**单例**、**瞬态**、**工厂**三种生命周期
  - 支持自动依赖注入
  - 提供全局容器实例

### 使用方式

```python
from app.di import DIContainer, IAIService

container = DIContainer()
ai_service = container.resolve(IAIService)
```

### 在 FastAPI 中使用

更新了 `app/dependencies.py`：

```python
def get_ai_service(
    container: DIContainer = Depends(get_container),
) -> IAIService:
    return container.resolve(IAIService)
```

### 路由更新

所有路由现在使用接口类型而非具体实现：

```python
@router.post("/", response_model=ThemeResponse)
async def create_theme(
    theme_data: ThemeCreate,
    service: IThemeService = Depends(get_theme_service),  # 使用接口
):
    return service.create(theme_data.name, theme_data.post_length)
```

---

## 3. AI 服务插件化架构

### 新增模块

#### `app/services/ai/plugin.py`
插件基类和元数据：

```python
@dataclass
class ProviderMetadata:
    name: str
    type: str
    version: str
    description: str
    requires_api_key: bool
    supports_stream: bool
    default_model: str
    configurable_params: Dict

class AIProvider(ABC):
    metadata: ProviderMetadata = None

    @abstractmethod
    def generate(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> str:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass
```

#### `app/services/ai/plugin_manager.py`
插件管理器：

- `register()` - 注册插件
- `unregister()` - 注销插件
- `get_provider_instance()` - 获取 Provider 实例
- `get_best_provider()` - 获取最佳可用 Provider
- `list_providers()` - 列出所有插件
- `discover_plugins()` - 自动发现插件
- `initialize_from_config()` - 从配置初始化

### 更新的 Provider

所有 Provider 现在包含元数据：

- **GLMProvider** - 智谱 GLM API
- **QwenProvider** - 通义千问 API
- **OllamaProvider** - Ollama 本地模型

### 扩展新 Provider

添加新的 AI Provider 非常简单：

```python
from app.services.ai.plugin import AIProvider, ProviderMetadata

class MyProvider(AIProvider):
    metadata = ProviderMetadata(
        name="My Provider",
        type="my",
        version="1.0.0",
        description="My custom AI provider",
        requires_api_key=True,
    )

    def generate(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> str:
        # 实现生成逻辑
        return "generated text"

    def test_connection(self) -> bool:
        # 实现连接测试
        return True

# 注册插件
from app.services.ai.plugin_manager import get_plugin_manager
manager = get_plugin_manager()
manager.register(MyProvider)
```

---

## 4. 单元测试

### 测试文件

- **`tests/test_validators.py`** - 验证器测试
- **`tests/test_di_container.py`** - DI 容器测试
- **`tests/test_plugin_system.py`** - 插件系统测试
- **`tests/test_schemas.py`** - Schema 验证测试
- **`tests/conftest.py`** - Pytest 配置和共享 fixtures

### 运行测试

```bash
# 使用脚本运行
./run_tests.sh

# 或直接使用 pytest
pytest tests/ -v --cov=app --cov-report=html
```

---

## 项目结构

```
app/
├── di/                          # 依赖注入模块
│   ├── __init__.py
│   ├── container.py            # DI 容器
│   └── interfaces.py           # 服务接口
├── validators/                  # 验证器模块
│   ├── __init__.py
│   ├── string_validator.py     # 字符串验证
│   └── business_validators.py  # 业务规则验证
├── services/
│   ├── ai/
│   │   ├── plugin.py           # 插件基类和元数据
│   │   ├── plugin_manager.py   # 插件管理器
│   │   ├── base.py             # 向后兼容的基类
│   │   ├── glm_provider.py     # GLM Provider
│   │   ├── qwen_provider.py    # Qwen Provider
│   │   └── ollama_provider.py  # Ollama Provider
│   └── ...
├── routers/
│   ├── themes.py               # 主题路由（使用接口）
│   ├── posts.py                # 帖子路由（使用接口）
│   └── corpus.py               # 语料库路由（使用接口）
├── dependencies.py             # 依赖注入配置
├── schemas.py                  # Pydantic 模型（集成验证）
└── ...

tests/
├── conftest.py                 # Pytest 配置
├── test_validators.py          # 验证器测试
├── test_di_container.py        # DI 容器测试
├── test_plugin_system.py       # 插件系统测试
└── test_schemas.py             # Schema 测试
```

---

## 向后兼容性

重构保持了向后兼容性：

1. **验证器** - 通过 Pydantic validator 集成，API 行为不变
2. **依赖注入** - 现有代码继续工作，只是底层实现变化
3. **插件系统** - 保留了 `create_provider()` 工厂函数

---

## 下一步建议

1. **集成测试** - 添加端到端集成测试
2. **性能测试** - 测试插件系统和 DI 容器的性能
3. **文档** - 添加更详细的 API 文档
4. **更多插件** - 添加更多 AI Provider（如 OpenAI、Claude）
5. **插件市场** - 考虑支持第三方插件
