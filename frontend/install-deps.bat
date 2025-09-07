@echo off
chcp 65001 >nul
echo.
echo 🚀 智能NPM依赖安装脚本
echo ================================
echo.

:: 设置变量
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

:: NPM源列表
set "SOURCES[0]=https://registry.npmmirror.com"
set "SOURCES[1]=https://repo.huaweicloud.com/repository/npm"
set "SOURCES[2]=https://mirrors.cloud.tencent.com/npm"
set "SOURCES[3]=https://registry.npmjs.org"

set "NAMES[0]=淘宝镜像"
set "NAMES[1]=华为云镜像"
set "NAMES[2]=腾讯云镜像"
set "NAMES[3]=NPM官方源"

echo 📦 开始安装前端依赖...
echo.

:: 尝试第一个源（淘宝镜像）
echo 🔄 尝试使用淘宝镜像安装...
call npm install --registry https://registry.npmmirror.com 2>nul
if %errorlevel%==0 (
    echo ✅ 使用淘宝镜像安装成功！
    goto success
)

:: 尝试第二个源（华为云）
echo 🔄 尝试使用华为云镜像安装...
call npm install --registry https://repo.huaweicloud.com/repository/npm 2>nul
if %errorlevel%==0 (
    echo ✅ 使用华为云镜像安装成功！
    goto success
)

:: 尝试第三个源（腾讯云）
echo 🔄 尝试使用腾讯云镜像安装...
call npm install --registry https://mirrors.cloud.tencent.com/npm 2>nul
if %errorlevel%==0 (
    echo ✅ 使用腾讯云镜像安装成功！
    goto success
)

:: 尝试官方源
echo 🔄 尝试使用NPM官方源安装...
call npm install 2>nul
if %errorlevel%==0 (
    echo ✅ 使用NPM官方源安装成功！
    goto success
)

:: 如果都失败了
echo ❌ 所有源都安装失败，请检查网络连接
echo.
echo 🔧 手动尝试方案：
echo    1. npm config set registry https://registry.npmmirror.com
echo    2. npm install
echo.
pause
exit /b 1

:success
echo.
echo 🎉 依赖安装完成！
echo.
echo 📋 接下来可以运行：
echo    npm run dev        # 启动开发服务器
echo    npm run build      # 构建生产版本
echo    npm run lint       # 代码检查
echo.
pause