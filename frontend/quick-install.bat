@echo off
echo 🚀 开始安装前端依赖...

:: 确保在正确的目录
if not exist "package.json" (
    echo ❌ 错误：找不到package.json文件
    echo 请确保在frontend目录下运行此脚本
    pause
    exit /b 1
)

echo 📦 清理npm缓存...
call npm cache clean --force

echo 🔄 尝试安装依赖（使用淘宝源）...
call npm install --registry https://registry.npmmirror.com --legacy-peer-deps
if %errorlevel%==0 (
    echo ✅ 依赖安装成功！
    echo.
    echo 🚀 现在可以运行：npm run dev
    pause
    exit /b 0
)

echo 🔄 尝试使用华为云源...
call npm install --registry https://repo.huaweicloud.com/repository/npm --legacy-peer-deps
if %errorlevel%==0 (
    echo ✅ 依赖安装成功！
    echo.
    echo 🚀 现在可以运行：npm run dev
    pause
    exit /b 0
)

echo ❌ 安装失败，尝试手动解决
echo.
echo 🔧 建议执行以下命令：
echo 1. npm cache clean --force
echo 2. npm install --legacy-peer-deps
echo 3. npm run dev
echo.
pause