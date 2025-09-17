@echo off
echo 🚀 启动智能监控预警系统后端服务...
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "backend\venv" (
    echo 📦 创建Python虚拟环境...
    python -m venv backend\venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call backend\venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装Python依赖包...
cd backend
pip install -r requirements.txt

REM 检查环境配置
if not exist ".env" (
    echo ⚙️ 创建环境配置文件...
    copy ..\env.example .env
    echo ✅ 已创建 .env 文件，请根据需要修改配置
)

REM 启动服务
echo 🚀 启动后端服务...
echo 📍 服务地址: http://localhost:8000
echo 📚 API文档: http://localhost:8000/api/docs
echo.
python main.py

pause
