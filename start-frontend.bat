@echo off
echo 🚀 启动智能监控预警系统前端服务...
echo.

REM 检查Node.js环境
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js未安装或未添加到PATH
    echo 请访问 https://nodejs.org 下载安装Node.js
    pause
    exit /b 1
)

REM 检查npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm未安装
    pause
    exit /b 1
)

REM 进入前端目录
cd frontend

REM 检查node_modules
if not exist "node_modules" (
    echo 📦 安装前端依赖包...
    npm install
)

REM 检查环境配置
if not exist ".env" (
    echo ⚙️ 创建前端环境配置...
    echo VITE_API_BASE_URL=http://localhost:8000/api/v1 > .env
    echo ✅ 已创建 .env 文件
)

REM 启动开发服务器
echo 🚀 启动前端开发服务器...
echo 📍 前端地址: http://localhost:3000
echo 🔗 后端API: http://localhost:8000/api/v1
echo.
npm run dev

pause
