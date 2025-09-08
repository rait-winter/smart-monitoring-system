# 智能监控预警系统 - 后端服务

基于FastAPI的高性能监控预警系统后端服务，提供AI驱动的异常检测、规则引擎和多渠道通知功能。

## 系统架构

```
├── API层 (FastAPI)
├── 服务层 (AI/ML, 规则引擎, 通知服务)
├── 数据访问层 (SQLAlchemy ORM)
├── 核心配置层 (Pydantic Settings)
└── 模型层 (Pydantic Schemas)
```

## 技术栈

- **框架**: FastAPI + Uvicorn
- **数据库**: PostgreSQL + SQLAlchemy 2.0
- **缓存**: Redis
- **AI/ML**: Scikit-learn, Pandas, NumPy
- **监控**: Prometheus
- **测试**: Pytest
- **部署**: Docker + Docker Compose

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd smart-monitoring-system/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
vim .env
```

### 3. 数据库初始化

```bash
# 初始化数据库表
python scripts/init-db.py
```

### 4. 启动开发服务器

```bash
# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

或者使用:

```bash
python main.py
```

## API文档

启动服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 项目结构

```
backend/
├── app/
│   ├── api/           # API路由
│   │   └── v1/
│   │       ├── endpoints/  # API端点
│   │       └── api.py      # API路由聚合
│   ├── core/          # 核心配置
│   ├── models/        # 数据模型和Schema
│   ├── services/      # 业务服务
│   └── utils/         # 工具函数
├── tests/             # 测试用例
├── scripts/           # 脚本工具
├── alembic/           # 数据库迁移
├── requirements.txt   # 依赖包
└── main.py           # 应用入口
```

## 核心功能

### 1. AI异常检测
- 多算法支持：孤立森林、Z-Score、统计学方法
- 时间序列预测
- 异常评分和严重程度评估

### 2. 规则引擎
- 灵活的规则条件配置
- 多条件组合逻辑
- 定时执行和事件触发

### 3. 通知服务
- 多渠道通知：Slack、邮件、Webhook
- 模板化消息
- 告警去重和重试机制

### 4. 指标查询
- Prometheus数据查询
- 范围查询和即时查询
- 指标元数据管理

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_system_api.py

# 生成测试覆盖率报告
pytest --cov=app --cov-report=html
```

## 部署

使用Docker Compose进行容器化部署：

```bash
# 在项目根目录运行
docker-compose up -d
```

## 数据库迁移

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "迁移描述"

# 应用迁移
alembic upgrade head
```

## 环境变量配置

关键配置项：

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| APP_NAME | 应用名称 | 智能监控预警系统 |
| DEBUG | 调试模式 | false |
| SECRET_KEY | 安全密钥 | 必须设置 |
| POSTGRES_SERVER | PostgreSQL服务器 | localhost |
| PROMETHEUS_URL | Prometheus地址 | http://localhost:9090 |

## 日志

系统使用结构化日志记录，支持JSON和文本格式：

```python
import structlog
logger = structlog.get_logger(__name__)
logger.info("操作成功", user_id=123, action="login")
```

## 性能监控

集成Prometheus监控：

- **指标端点**: http://localhost:8000/metrics
- **健康检查**: http://localhost:8000/health

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查.env中的数据库配置
   - 确保PostgreSQL服务正在运行

2. **Prometheus连接失败**
   - 检查PROMETHEUS_URL配置
   - 确保Prometheus服务可访问

3. **AI模型加载失败**
   - 检查AI_MODEL_PATH配置
   - 确保模型文件存在

### 调试技巧

```bash
# 启用调试模式
export DEBUG=true

# 查看详细日志
tail -f logs/app.log
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 许可证

MIT License