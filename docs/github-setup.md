# GitHub 代码上传指南

本文档记录了将智能监控系统代码上传到GitHub的完整流程。

## 项目信息

- **项目名称**: Smart Monitoring System
- **GitHub仓库**: https://github.com/rait-winter/smart-monitoring-system.git
- **项目描述**: AI-driven anomaly detection and intelligent monitoring system with Vue 3 + Python FastAPI

## 上传流程

### 1. 初始化Git仓库

首先在项目根目录初始化Git仓库：

```bash
# 进入项目目录
cd d:\autocode\20250902

# 初始化Git仓库
git init
```

### 2. 创建.gitignore文件

创建`.gitignore`文件以排除不需要上传的文件：

```gitignore
# Dependencies
node_modules/
*/node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
package-lock.json
yarn.lock

# Build outputs
dist/
build/
.output/
.vite/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
Thumbs.db

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/
.pytest_cache/
.coverage
htmlcov/

# Docker
.dockerignore

# Logs
logs/
*.log

# Database
*.db
*.sqlite
*.sqlite3

# Monitoring data
monitoring_data/
prometheus_data/
```

### 3. 添加文件到暂存区

将所有项目文件添加到Git暂存区：

```bash
git add .
```

### 4. 创建初始提交

创建项目的初始提交：

```bash
git commit -m "Initial commit: Smart Monitoring System with AI-driven anomaly detection"
```

### 5. 在GitHub上创建仓库

1. 访问 [GitHub](https://github.com)
2. 登录账户
3. 点击右上角的 "+" 号，选择 "New repository"
4. 填写仓库信息：
   - **仓库名称**: `smart-monitoring-system`
   - **描述**: `AI-driven anomaly detection and intelligent monitoring system with Vue 3 + Python FastAPI`
   - **可见性**: 根据需要选择 Public 或 Private
   - **重要**: 不要勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

### 6. 关联远程仓库并推送

```bash
# 添加远程仓库
git remote add origin https://github.com/rait-winter/smart-monitoring-system.git

# 将主分支重命名为main
git branch -M main

# 推送代码到GitHub
git push -u origin main
```

## 推送结果

成功推送后的统计信息：
- **提交数**: 1个初始提交
- **文件数**: 68个文件
- **代码行数**: 9,440行插入
- **分支**: main分支已设置为跟踪远程origin/main

## 后续操作

### 日常开发流程

```bash
# 查看当前状态
git status

# 添加修改的文件
git add <file>  # 或 git add . 添加所有修改

# 提交更改
git commit -m "描述性的提交信息"

# 推送到远程仓库
git push origin main
```

### 分支管理

```bash
# 创建新分支
git checkout -b feature/new-feature

# 切换分支
git checkout main

# 合并分支
git merge feature/new-feature

# 删除本地分支
git branch -d feature/new-feature
```

### 同步远程更改

```bash
# 拉取远程更改
git pull origin main

# 获取远程分支信息
git fetch origin
```

## 项目结构说明

上传到GitHub的项目包含以下主要组件：

### 后端服务 (backend/)
- **技术栈**: Python 3.11 + FastAPI + SQLAlchemy 2.0
- **核心模块**: 
  - API端点 (api/v1/endpoints/)
  - 核心配置 (core/)
  - 业务服务 (services/)
  - 数据模型 (models/)

### 前端应用 (frontend/)
- **技术栈**: Vue 3 + TypeScript + Element Plus + ECharts 5
- **构建工具**: Vite
- **核心模块**:
  - 组件库 (src/components/)
  - 页面视图 (src/views/)
  - 路由配置 (src/router/)
  - 工具函数 (src/utils/)

### 部署配置
- **容器化**: Docker + Docker Compose
- **文档**: 架构文档和部署指南
- **脚本**: 自动化设置脚本

## 注意事项

1. **环境文件**: `.env`文件已被忽略，需要根据`.env.example`创建本地环境配置
2. **依赖安装**: 首次克隆后需要安装前后端依赖
3. **版本控制**: 遵循语义化版本控制规范
4. **代码规范**: 
   - Python: Black + Flake8 + MyPy
   - Vue: ESLint + Prettier + TypeScript
5. **测试覆盖率**: 目标单元测试覆盖率 > 90%

## 相关链接

- [项目架构文档](./architecture.md)
- [部署指南](./deployment.md)
- [API文档](./api.md)
- [GitHub仓库](https://github.com/rait-winter/smart-monitoring-system)

---

*文档创建时间: 2025-09-07*  
*最后更新: 2025-09-07*