#!/bin/bash
# 智能NPM依赖安装脚本 - Linux/Mac版本

echo "🚀 智能NPM依赖安装脚本"
echo "================================"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# NPM源列表
declare -a SOURCES=(
    "https://registry.npmmirror.com"
    "https://repo.huaweicloud.com/repository/npm" 
    "https://mirrors.cloud.tencent.com/npm"
    "https://registry.npmjs.org"
)

declare -a NAMES=(
    "淘宝镜像"
    "华为云镜像"
    "腾讯云镜像" 
    "NPM官方源"
)

echo "📦 开始安装前端依赖..."
echo ""

# 尝试每个源
for i in "${!SOURCES[@]}"; do
    echo "🔄 尝试使用${NAMES[$i]}安装..."
    
    if npm install --registry "${SOURCES[$i]}" > /dev/null 2>&1; then
        echo "✅ 使用${NAMES[$i]}安装成功！"
        echo ""
        echo "🎉 依赖安装完成！"
        echo ""
        echo "📋 接下来可以运行："
        echo "   npm run dev        # 启动开发服务器"
        echo "   npm run build      # 构建生产版本"
        echo "   npm run lint       # 代码检查"
        echo ""
        exit 0
    fi
done

# 如果都失败了
echo "❌ 所有源都安装失败，请检查网络连接"
echo ""
echo "🔧 手动尝试方案："
echo "   1. npm config set registry https://registry.npmmirror.com"
echo "   2. npm install"
echo ""
exit 1