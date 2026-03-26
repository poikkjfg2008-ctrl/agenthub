#!/bin/bash

# AI Portal 启动脚本
# 用于快速启动所有服务

set -e

echo "🚀 启动 AI Portal..."

# 检查 Python 版本
if command -v /home/yy/python312/bin/python &> /dev/null; then
    PYTHON_BIN="/home/yy/python312/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="$(command -v python3)"
elif command -v python &> /dev/null; then
    PYTHON_BIN="$(command -v python)"
else
    echo "❌ Python 未找到，请安装 Python 3.12+"
    exit 1
fi

echo "✅ 使用 Python: $PYTHON_BIN"

# 检查 Node.js 版本
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未找到"
    exit 1
fi

# 进入项目根目录
cd "$(dirname "$0")/.."

# 创建日志目录
mkdir -p logs

# 检查 .env 文件
if [ ! -f "backend/.env" ]; then
    echo "⚠️  未找到 backend/.env 文件，从示例创建..."
    cp .env.example backend/.env
    echo "✅ 已创建 backend/.env，请根据需要修改配置"
fi

# 启动前置检查（OpenCode / OpenWork / WebSDK 端点）
echo "🔍 执行启动前置检查..."
if ! $PYTHON_BIN scripts/preflight_check.py; then
    echo "❌ 前置检查未通过，请先按文档启动 OpenCode/OpenWork 并检查端点配置"
    exit 1
fi

echo "✅ 前置检查通过"

# 启动后端
echo "📦 启动后端服务..."
cd backend

# 检查依赖
if [ ! -d "venv" ]; then
    echo "📥 安装 Python 依赖..."
    $PYTHON_BIN -m pip install -r requirements.txt
fi

# 启动后端服务 (后台运行)
echo "🔧 启动 FastAPI 服务在 http://localhost:8000"
# Note: --reload is disabled by default to avoid event loop issues with httpx AsyncClient
# Set RELOAD=true to enable for development
if [ "${RELOAD:-false}" = "true" ]; then
    $PYTHON_BIN -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
else
    $PYTHON_BIN -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
fi
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 检查后端是否成功启动
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo "❌ 后端启动失败，查看日志: logs/backend.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ 后端服务启动成功"

# 启动前端
cd ../frontend

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📥 安装 Node.js 依赖..."
    npm install
fi

# 启动前端服务 (后台运行)
echo "🎨 启动前端服务在 http://localhost:5173"
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# 等待前端启动
sleep 3

# 检查前端是否成功启动
if ! curl -s http://localhost:5173 > /dev/null; then
    echo "⚠️  前端可能还在启动中，请稍后访问 http://localhost:5173"
fi

echo "✅ 前端服务启动成功"

# 保存 PID 到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "🎉 AI Portal 启动完成!"
echo ""
echo "📍 访问地址:"
echo "   前端: http://localhost:5173"
echo "   后端 API: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "📋 进程 ID:"
echo "   后端: $BACKEND_PID"
echo "   前端: $FRONTEND_PID"
echo ""
echo "📝 日志文件:"
echo "   后端: logs/backend.log"
echo "   前端: logs/frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   ./scripts/stop.sh"
echo ""
echo "💡 提示: 首次访问会自动跳转到模拟登录页面"
