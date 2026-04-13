# 用户系统使用指南

## 概述

用车总结生成器现已支持用户系统，通过手机号和密码登录，确保语料库数据完全隔离，任何情况下都不会被清空。

## 快速开始

### 1. 启动服务

```bash
# 安装依赖（如果尚未安装）
pip install bcrypt python-jose

# 执行数据库迁移
python app/database_migration.py

# 启动应用
python run_app.py
```

### 2. 访问地址

- **登录页面**: http://localhost:8501 (运行 `streamlit run frontend/login_page.py`)
- **API文档**: http://localhost:8000/docs

## 功能特性

### 🔐 用户认证

- **用户注册**: 使用手机号注册账号
- **用户登录**: 手机号 + 密码登录
- **JWT认证**: 安全的令牌认证机制
- **自动登出**: 超时自动退出，可手动登出

### 📚 语料库管理

- **完全隔离**: 每个用户的语料库互不可见
- **永久保存**: 语料库数据不会被清空
- **风格分析**: 基于用户自己的语料库分析写作风格
- **批量操作**: 支持添加、编辑、删除语料

### 🎨 写作风格分析

- **个性化风格**: 每个用户独立的风格特征
- **智能学习**: AI分析用户的写作习惯和特点
- **持续优化**: 随着语料增加，风格分析更准确

## API 接口

### 认证相关

```bash
# 注册用户
POST /api/auth/register
{
    "phone": "13800138000",
    "password": "123456",
    "nickname": "用户昵称（可选）"
}

# 用户登录
POST /api/auth/login
{
    "phone": "13800138000",
    "password": "123456"
}

# 获取当前用户信息
GET /api/auth/me
Authorization: Bearer <token>

# 用户登出
POST /api/auth/logout
Authorization: Bearer <token>
```

### 语料库相关

```bash
# 添加语料
POST /api/corpus/
Authorization: Bearer <token>
{
    "title": "帖子标题",
    "content": "帖子内容",
    "tags": "标签1,标签2",
    "note": "备注"
}

# 获取语料列表
GET /api/corpus/?skip=0&limit=20&tag=标签
Authorization: Bearer <token>

# 分析写作风格
POST /api/corpus/analyze-style
Authorization: Bearer <token>

# 获取风格特征
GET /api/corpus/style-profile
Authorization: Bearer <token>
```

## 数据库结构

### users 表
- id: 用户ID
- phone: 手机号（唯一）
- password_hash: 密码哈希
- nickname: 昵称
- email: 邮箱
- is_active: 是否激活
- is_verified: 是否验证
- created_at: 创建时间
- updated_at: 更新时间

### user_posts 表
- id: 帖子ID
- user_id: 用户ID（外键）
- title: 标题
- content: 内容
- tags: 标签
- note: 备注
- is_public: 是否公开
- view_count: 浏览次数
- created_at: 创建时间
- updated_at: 更新时间

### style_profile 表
- id: 特征ID
- user_id: 用户ID（外键）
- content: 风格特征描述
- post_count: 分析使用的帖子数
- model_used: 使用的模型
- confidence_score: 置信度
- created_at: 创建时间
- updated_at: 更新时间

### user_sessions 表
- id: 会话ID
- user_id: 用户ID（外键）
- session_token: 会话令牌
- expires_at: 过期时间
- device_info: 设备信息
- ip_address: IP地址
- created_at: 创建时间
- last_active: 最后活跃时间

### password_reset_tokens 表
- id: 令牌ID
- user_id: 用户ID（外键）
- token: 重置令牌
- expires_at: 过期时间
- is_used: 是否已使用
- created_at: 创建时间

## 安全特性

1. **密码安全**
   - 使用 bcrypt 加密存储密码
   - 密码长度限制（6-20位）
   - 手机号格式验证

2. **会话管理**
   - JWT 令牌认证
   - 令牌过期机制（默认30分钟）
   - 自动清理过期会话

3. **数据隔离**
   - 用户数据完全隔离
   - 语料库严格绑定用户
   - API调用需要认证

4. **输入验证**
   - 防止 XSS 攻击
   - 防止 SQL 注入
   - 内容长度限制

## 迁移说明

### 从旧版本迁移

1. **数据库升级**
   - 已自动执行迁移脚本
   - 添加了用户相关表
   - 为现有语料库添加了 user_id 列

2. **数据分配**
   - 现有语料库已分配给默认用户（ID: 1）
   - 可以继续使用所有历史数据

## 故障排除

### 常见问题

1. **无法启动应用**
   - 检查端口是否被占用
   - 确保 Python 3.8+ 已安装
   - 检查依赖是否完整

2. **登录失败**
   - 检查手机号格式
   - 确认密码正确
   - 检查账户是否被禁用

3. **语料库为空**
   - 确认已登录
   - 检查是否有语料添加权限
   - 查看 API 日志

### 日志查看

```bash
# 查看应用日志
tail -f app.log

# 查看 Streamlit 日志
streamlit run frontend/login_page.py
```

## 下一步计划

1. **短信验证**
   - 集成短信验证码
   - 手机号验证功能

2. **第三方登录**
   - 微信登录
   - 支付宝登录

3. **数据导出**
   - 导出个人语料库
   - 导出分析报告

4. **高级功能**
   - 语料库分享
   - 协作编辑
   - AI 辅助优化

## 技术栈

- **后端**: FastAPI + SQLAlchemy
- **前端**: Streamlit
- **数据库**: SQLite
- **认证**: JWT + bcrypt
- **AI**: Ollama / API 模型