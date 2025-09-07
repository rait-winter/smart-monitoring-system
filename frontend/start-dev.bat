@echo off
echo 🚀 启动前端开发服务器（简化模式）

cd /d "d:\autocode\20250902\frontend"

echo 📦 检查依赖...
if not exist "node_modules\" (
    echo ⚠️  依赖未安装，开始安装...
    call npm install --registry https://registry.npmmirror.com --legacy-peer-deps
)

echo 🔄 启动开发服务器...
call npm run dev

pause