#!/bin/bash

# AI Portal 后端测试脚本

echo "🧪 开始运行后端 API 测试..."
echo ""

cd /home/yy/agenthub/backend

# 检查服务是否运行
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo "❌ 后端服务未运行，请先启动服务"
    exit 1
fi

echo "✅ 后端服务正在运行"
echo ""

# 运行测试
/home/yy/python312/bin/python tests/test_api.py

echo ""
echo "测试完成！"
