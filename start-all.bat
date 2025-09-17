@echo off
echo 🚀 启动智能监控预警系统 (全栈)
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)

REM 检查Node.js环境
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js未安装或未添加到PATH
    echo 请访问 https://nodejs.org 下载安装Node.js
    pause
    exit /b 1
)

echo 📋 系统要求检查完成
echo.

REM 启动后端服务
echo 🔧 启动后端服务...
start "后端服务" cmd /k "cd /d %~dp0 && call start-backend.bat"

REM 等待后端启动
echo ⏳ 等待后端服务启动...
timeout /t 5 /nobreak >nul

REM 启动前端服务
echo 🎨 启动前端服务...
start "前端服务" cmd /k "cd /d %~dp0 && call start-frontend.bat"

echo.
echo ✅ 服务启动完成！
echo 📍 前端地址: http://localhost:3000
echo 📍 后端地址: http://localhost:8000
echo 📚 API文档: http://localhost:8000/api/docs
echo.
echo 按任意键关闭此窗口...
pause >nul
