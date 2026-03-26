#!/bin/bash

# AI Portal 完整测试脚本

echo "🧪 AI Portal 系统测试"
echo "=================="
echo ""

# 检查服务状态
echo "1️⃣ 检查服务状态..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ 后端服务运行中"
else
    echo "❌ 后端服务未运行"
    echo "请先启动服务: ./scripts/start.sh"
    exit 1
fi

if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ 前端服务运行中"
else
    echo "❌ 前端服务未运行"
    echo "请先启动服务: ./scripts/start.sh"
    exit 1
fi

echo ""
echo "2️⃣ 运行后端测试..."
cd /home/yy/agenthub/backend
/home/yy/python312/bin/python tests/test_api_simple.py

echo ""
echo "3️⃣ 前端测试..."
echo "📱 请在浏览器中打开: http://localhost:5173/index.test.html"
echo "   然后点击'运行测试'按钮"

echo ""
echo "=================="
echo "✅ 测试完成！"
echo ""
echo "📊 查看详细测试报告: TEST_REPORT.md"
