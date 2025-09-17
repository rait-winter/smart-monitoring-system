@echo off
echo 🚀 智能监控预警系统 - 依赖安装脚本
echo.

REM 检查Python环境
echo 📋 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请访问 https://python.org 下载安装Python 3.11+
    pause
    exit /b 1
) else (
    echo ✅ Python环境正常
)

REM 检查Node.js环境
echo 📋 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js未安装或未添加到PATH
    echo 请访问 https://nodejs.org 下载安装Node.js 22.11+
    pause
    exit /b 1
) else (
    echo ✅ Node.js环境正常
)

echo.
echo 📦 开始安装依赖...

REM 安装后端依赖
echo 🔧 安装后端Python依赖...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
cd ..

REM 安装前端依赖
echo 🎨 安装前端Node.js依赖...
cd frontend
npm install
cd ..

REM 创建环境配置文件
echo ⚙️ 创建环境配置文件...
if not exist "backend\.env" (
    copy env.example backend\.env
    echo ✅ 已创建后端环境配置
)

if not exist "frontend\.env" (
    echo VITE_API_BASE_URL=http://localhost:8000/api/v1 > frontend\.env
    echo ✅ 已创建前端环境配置
)

echo.
echo ✅ 依赖安装完成！
echo.
echo 🚀 现在可以运行以下命令启动服务：
echo   - 启动后端: start-backend.bat
echo   - 启动前端: start-frontend.bat
echo   - 启动全部: start-all.bat
echo.
pause
