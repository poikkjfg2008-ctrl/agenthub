#!/bin/bash

# AI Portal 停止脚本

echo "🛑 停止 AI Portal..."

cd "$(dirname "$0")/.."

# 读取 PID 文件
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo "停止后端服务 (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "后端进程已停止"
    rm .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    echo "停止前端服务 (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "前端进程已停止"
    rm .frontend.pid
fi

# 清理可能残留的进程
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo "✅ AI Portal 已停止"
