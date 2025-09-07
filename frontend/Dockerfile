# Node.js 22.11 官方镜像 - 构建阶段
FROM node:22.11-alpine as build-stage

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build:prod

# Nginx 生产镜像
FROM nginx:1.25-alpine as production-stage

# 安装必要工具
RUN apk add --no-cache curl

# 复制构建结果
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制Nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]