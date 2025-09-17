#!/bin/bash

echo "🚀 启动智能监控预警系统后端服务..."
echo

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装或未添加到PATH"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "backend/venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv backend/venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source backend/venv/bin/activate

# 安装依赖
echo "📥 安装Python依赖包..."
cd backend
pip install -r requirements.txt

# 检查环境配置
if [ ! -f ".env" ]; then
    echo "⚙️ 创建环境配置文件..."
    cp ../env.example .env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
fi

# 启动服务
echo "🚀 启动后端服务..."
echo "📍 服务地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/api/docs"
echo
python main.py
