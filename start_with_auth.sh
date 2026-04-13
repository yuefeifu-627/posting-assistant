#!/bin/bash

# 启动带用户系统的应用

echo "🚀 正在启动带用户系统的用车总结生成器..."

# 检查并创建数据库迁移
echo "📝 正在执行数据库迁移..."
python app/database_migration.py

# 启动后端服务
echo "🔧 正在启动FastAPI后端服务..."
uvicorn app.main:app --reload &
BACKEND_PID=$!

# 等待后端服务启动
sleep 3

# 启动前端（带完整功能的登录界面）
echo "🌐 正在启动Streamlit前端..."
streamlit run frontend/app_with_login.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "✅ 服务启动成功！"
echo "🔗 访问地址:"
echo "   - 前端登录页面: http://localhost:8501"
echo "   - API文档: http://localhost:8000/docs"
echo ""
echo "📋 使用说明:"
echo "1. 首先访问前端页面进行注册或登录"
echo "2. 登录成功后即可使用所有功能"
echo ""
echo "⚠️  如需停止服务，请按 Ctrl+C"

# 等待用户中断
wait

# 清理进程
echo "🛑 正在停止服务..."
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
echo "✅ 服务已停止"