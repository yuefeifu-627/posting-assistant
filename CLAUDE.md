# Zeeker App Assistant - 项目文档

## 项目概述

基于 AI 的用车总结文章生成工具，使用 FastAPI 后端 + Streamlit 前端。

## 架构

### 技术栈
- **后端**: FastAPI + SQLAlchemy + SQLite
- **前端**: Streamlit
- **AI Provider**: 插件式架构，支持 Ollama (本地)、GLM、MiniMax

### AI Provider 插件系统
AI Provider 通过 `PluginManager` 动态加载，位于 `app/services/ai/` 目录：

| Provider | 类型 | 用途 |
|----------|------|------|
| `OllamaProvider` | 本地模型 | 默认，零成本 |
| `GLMProvider` | 云端 GLM-4 | 云端备选 |
| `MiniMaxProvider` | 云端 MiniMax-Text-01 | 主要云端选择 |

**优先级**: 风格分析优先 MiniMax > GLM > Ollama；生成帖子由用户选择。

### 依赖注入
使用手写 DI 容器 (`app/di/container.py`)，通过 `app/dependencies.py` 与 FastAPI 的 `Depends` 集成。

**注意**: DI 容器只管理 Service 层。Repository 在 Service 内部直接创建，db session 由 FastAPI 的 `Depends(get_db)` 注入到 Service 构造函数。

### 数据库
- `app/models.py` - 主题/帖子数据模型
- `app/models_user.py` - 用户认证数据模型
- `app/database.py` - SQLAlchemy 配置，`get_db()` 是生成器函数

## 配置 (.env)

```env
# 数据库（可选，默认 data/posts.db）
DATABASE_URL=sqlite:///...

# Ollama 本地模型
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:9b

# MiniMax API（推荐用于云端）
MINMAX_API_KEY=your_key_here
MINMAX_MODEL=MinMax-Text-01

# GLM API
GLM_API_KEY=your_key_here
GLM_MODEL=glm-4v

# JWT（生产环境必须修改！）
SECRET_KEY=your-secret-key-here
```

## 新增 AI Provider

1. 在 `app/services/ai/` 创建 `{name}_provider.py`
2. 继承 `AIProvider` 基类，定义 `metadata`
3. 实现 `generate()` 和 `test_connection()` 方法
4. 在 `AIService._register_builtin_plugins()` 中注册

## 安全注意事项

1. **JWT SECRET_KEY**: 部署时必须替换默认值 `"your-secret-key-here"`，否则 token 可被伪造
2. **CORS**: 当前允许所有来源 (`allow_origins=["*"]`)，生产环境应限制
3. **Token 传递**: 前端通过 URL query param 传递 token（见 `frontend/app_with_login.py`），生产环境应改用 HttpOnly cookie
4. **敏感信息**: `.env` 不提交到版本控制

## 常见问题

### AI 生成调用了错误的 Provider
检查:
1. `.env` 中 API Key 是否正确配置
2. 前端选择的模型与 backend 传递的 `api_type` 是否一致
3. `AIService.check_api_config()` 返回的 `glm_configured` / `minmax_configured` 状态

### 风格分析报错
检查 `CorpusServiceUser` 是否收到了 `ai_service` 实例（不是 `None`）。相关路由: `app/routers/corpus_user.py`

### 数据库 session 泄漏
DI 容器的 Repository 工厂每次 `resolve()` 创建新 session。当前架构下每个请求可能产生多个 session（一个来自 FastAPI `Depends(get_db)`，多个来自容器内部工厂）。如遇 session 问题，检查 `app/di/container.py` 的 `_register_defaults()` 方法。
