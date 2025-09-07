@echo off
echo 启动智能监控预警系统前端...
echo.

cd /d "d:\autocode\20250902\frontend"

echo 当前目录: %CD%
echo.

echo 启动开发服务器...
npm run dev

pause