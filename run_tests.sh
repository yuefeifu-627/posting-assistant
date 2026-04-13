#!/bin/bash

# 测试运行脚本

echo "🧪 开始运行测试..."

# 检查是否安装了 pytest
if ! command -v pytest &> /dev/null
then
    echo "❌ pytest 未安装，正在安装..."
    pip install pytest pytest-cov
fi

# 运行测试
echo ""
echo "📋 运行所有测试..."
pytest tests/ -v --tb=short --cov=app --cov-report=html --cov-report=term

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 所有测试通过！"
    echo "📊 覆盖率报告已生成: htmlcov/index.html"
else
    echo ""
    echo "❌ 部分测试失败，请检查输出。"
    exit 1
fi
