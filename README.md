# 用车总结生成器

基于FastAPI + Streamlit + Ollama的AI用车总结文章生成工具。

## 功能特点

- 📝 基于主题生成用车总结文章
- 🤖 使用本地Ollama模型（qwen3.5:9b）
- 📂 主题管理：创建主题、保存参考帖子
- 💾 SQLite数据库存储历史记录
- ✏️ 支持编辑已生成的帖子
- 🎨 简洁的Streamlit Web界面

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑.env文件，根据需要修改配置
```

### 3. 启动Ollama服务

确保Ollama服务正在运行，并且qwen3.5:9b模型已安装：

```bash
# 检查Ollama服务
ollama list

# 如果没有模型，拉取模型
ollama pull qwen3.5:9b
```

### 4. 启动应用

启动后端服务：
```bash
uvicorn app.main:app --reload
```

启动前端界面（新终端）：
```bash
streamlit run frontend/app.py
```

访问 http://localhost:8501 使用Web界面。

## 项目结构

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── models.py            # 数据库模型
│   ├── database.py          # 数据库连接
│   ├── schemas.py           # Pydantic模型
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── posts.py         # 文章相关API
│   │   └── upload.py        # 文件上传API
│   └── services/
│       ├── __init__.py
│       └── ai_service.py    # Ollama AI调用
├── frontend/
│   └── app.py               # Streamlit应用
├── uploads/                 # 图片存储目录
├── data/
│   └── posts.db             # SQLite数据库
├── requirements.txt
├── .env.example
└── README.md
```

## API文档

启动后端服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 使用说明

1. **创建主题** - 在左侧侧边栏点击"创建新主题"
2. **设置参考** - 可粘贴热门帖子作为风格参考（可选）
3. **生成帖子** - 选择主题后，填写额外信息，点击生成
4. **编辑修改** - 在生成的帖子基础上编辑完善
5. **查看历史** - 同一主题下可查看多篇帖子

## 技术栈

- **后端**: FastAPI
- **前端**: Streamlit
- **AI模型**: Ollama (qwen3.5:9b)
- **数据库**: SQLite + SQLAlchemy
- **文件存储**: 本地文件系统
