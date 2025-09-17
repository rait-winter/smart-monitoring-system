#!/bin/bash

echo "🚀 启动智能监控预警系统前端服务..."
echo

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装或未添加到PATH"
    echo "请访问 https://nodejs.org 下载安装Node.js"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm未安装"
    exit 1
fi

# 进入前端目录
cd frontend

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖包..."
    npm install
fi

# 检查环境配置
if [ ! -f ".env" ]; then
    echo "⚙️ 创建前端环境配置..."
    echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" > .env
    echo "✅ 已创建 .env 文件"
fi

# 启动开发服务器
echo "🚀 启动前端开发服务器..."
echo "📍 前端地址: http://localhost:3000"
echo "🔗 后端API: http://localhost:8000/api/v1"
echo
npm run dev
