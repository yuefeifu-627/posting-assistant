#!/bin/bash

echo "🚗 启动用车总结生成器..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "安装依赖..."
    pip install -r requirements.txt
fi

# 检查Ollama
echo "🤖 检查Ollama服务..."
if ! ollama list &> /dev/null; then
    echo "⚠️  Ollama服务未启动，请先运行: ollama serve"
    exit 1
fi

# 启动后端
echo "🔧 启动FastAPI后端..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动Streamlit前端..."
streamlit run frontend/app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "✅ 服务已启动!"
echo "   - 后端API: http://localhost:8000"
echo "   - 前端界面: http://localhost:8501"
echo "   - API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务..."

# 等待用户中断
trap "echo '停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT
wait