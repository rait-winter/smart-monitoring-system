# 智能监控预警系统 - 后端运行测试操作指南

本文档详细说明了如何运行、测试和调试智能监控预警系统的后端服务。

## 目录

1. [环境准备](#环境准备)
2. [项目启动](#项目启动)
3. [配置管理](#配置管理)
4. [数据库操作](#数据库操作)
5. [测试运行](#测试运行)
6. [API文档](#api文档)
7. [日志查看](#日志查看)
8. [性能监控](#性能监控)
9. [故障排除](#故障排除)

## 环境准备

### 1. Python环境

项目需要Python 3.11版本运行环境，推荐使用conda创建和管理虚拟环境：

```bash
# 创建conda环境
conda create -n smart-monitoring python=3.11

# 激活环境
conda activate smart-monitoring

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境变量配置

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件
vim .env  # 或使用其他编辑器
```

关键配置项：
- `DATABASE_URL`: 数据库连接URL
- `SECRET_KEY`: 安全密钥（必须设置）
- `PROMETHEUS_URL`: Prometheus服务地址

### 3. 数据库准备

项目支持两种数据库配置：
1. **开发环境**: SQLite（默认）
2. **生产环境**: PostgreSQL

开发环境会自动使用SQLite数据库，无需额外配置PostgreSQL。

## 项目启动

### 1. 开发模式启动

```bash
# 激活conda环境
conda activate smart-monitoring

# 启动开发服务器
python main.py
```

或者使用uvicorn直接启动：

```bash
# 使用uvicorn启动（带热重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 生产模式启动

```bash
# 使用Gunicorn启动（推荐用于生产环境）
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### 3. Docker启动

```bash
# 在项目根目录运行
docker-compose up -d
```

## 配置管理

### 1. 配置文件

项目支持多种配置文件：
- `.env`: 主配置文件
- `.env.development`: 开发环境配置
- `.env.production`: 生产环境配置

### 2. 配置验证

创建测试脚本验证配置加载：

```python
# test_config.py
import os
from dotenv import load_dotenv

# 加载环境变量
env_files = [".env", ".env.development", "../.env", "../.env.development"]
for env_file in env_files:
    if os.path.exists(env_file):
        load_dotenv(env_file)
        break

from app.core.config import settings
print(f"应用名称: {settings.APP_NAME}")
print(f"数据库URL: {settings.DATABASE_URL}")
print(f"环境: {settings.ENVIRONMENT}")
```

运行验证脚本：

```bash
python test_config.py
```

## 数据库操作

### 1. 数据库初始化

```bash
# 初始化数据库表
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 2. 数据库迁移

使用Alembic进行数据库迁移：

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "迁移描述"

# 应用迁移
alembic upgrade head
```

### 3. 数据库连接测试

创建数据库连接测试脚本：

```python
# test_db_connection.py
import asyncio
import sys
import os

# 加载环境变量
from dotenv import load_dotenv
env_files = [".env", ".env.development", "../.env", "../.env.development"]
for env_file in env_files:
    if os.path.exists(env_file):
        load_dotenv(env_file)
        break

from app.core.config import settings
from app.core.database import engine

async def test_connection():
    try:
        async with engine.begin() as conn:
            print("✅ 数据库连接成功!")
            from sqlalchemy import text
            result = await conn.execute(text("SELECT 1"))
            print(f"查询结果: {result.scalar()}")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
```

运行测试脚本：

```bash
python test_db_connection.py
```

## 测试运行

### 1. 运行所有测试

```bash
# 运行所有测试
pytest

# 生成详细输出
pytest -v

# 生成测试覆盖率报告
pytest --cov=app --cov-report=html
```

### 2. 运行特定测试

```bash
# 运行特定测试文件
pytest tests/test_system_api.py

# 运行特定测试类
pytest tests/test_system_api.py::TestSystemAPI

# 运行特定测试方法
pytest tests/test_system_api.py::TestSystemAPI::test_health_check
```

### 3. 异步测试

项目使用pytest-asyncio支持异步测试：

```bash
# 运行异步测试
pytest tests/test_anomaly_detection.py -v
```

### 4. 测试结构

```
tests/
├── test_anomaly_detection.py    # 异常检测API测试
├── test_metrics_api.py          # 指标查询API测试
└── test_system_api.py           # 系统管理API测试
```

## API文档

启动服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

健康检查端点：
- **健康检查**: http://localhost:8000/health

## 日志查看

系统使用结构化日志记录，支持JSON和文本格式：

```bash
# 查看日志文件
tail -f logs/app.log

# 或者在开发环境中查看控制台输出
```

日志配置在.env文件中：
- `LOG_LEVEL`: 日志级别（DEBUG, INFO, WARNING, ERROR）
- `LOG_FORMAT`: 日志格式（json或text）
- `LOG_FILE`: 日志文件路径

## 性能监控

集成Prometheus监控：

- **指标端点**: http://localhost:8000/metrics
- **健康检查**: http://localhost:8000/health

## 故障排除

### 1. 常见问题

#### 数据库连接失败
```bash
# 检查数据库URL配置
echo $DATABASE_URL

# 测试数据库连接
python test_db_connection.py
```

#### 环境变量未加载
```bash
# 验证环境变量
python -c "import os; print('DATABASE_URL:', os.getenv('DATABASE_URL'))"

# 检查配置加载
python test_config.py
```

#### 依赖包缺失
```bash
# 重新安装依赖
pip install -r requirements.txt

# 或者安装特定包
pip install aiosqlite==0.19.0
```

### 2. 调试技巧

#### 启用调试模式
```bash
# 设置环境变量
export DEBUG=true
export LOG_LEVEL=DEBUG
```

#### 查看详细日志
```bash
# 查看实时日志
tail -f logs/app.log

# 或者在控制台查看输出
python main.py
```

### 3. 配置验证脚本

创建完整的配置验证脚本：

```python
# full_debug.py
import os
from dotenv import load_dotenv

print("=== 环境变量加载阶段 ===")
# 加载环境变量
env_files = [".env", ".env.development", "../.env", "../.env.development"]
loaded_env = None
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"加载环境文件: {env_file}")
        load_dotenv(env_file)
        loaded_env = env_file
        break

print("环境变量检查:")
print(f"  DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT')}")

print("\n=== Pydantic配置加载阶段 ===")
try:
    from app.core.config import Settings
    settings = Settings()
    print(f"配置实例 DATABASE_URL: {settings.DATABASE_URL}")
    print(f"配置实例 ENVIRONMENT: {settings.ENVIRONMENT}")
    
    print("\n=== 全局设置检查 ===")
    from app.core.config import settings as global_settings
    print(f"全局设置 DATABASE_URL: {global_settings.DATABASE_URL}")
    print(f"全局设置 ENVIRONMENT: {global_settings.ENVIRONMENT}")
    
except Exception as e:
    print(f"配置加载失败: {e}")
    import traceback
    traceback.print_exc()
```

运行调试脚本：

```bash
python full_debug.py
```

## 附录

### 1. 项目结构

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

### 2. 核心服务

- **AI异常检测**: 多算法支持（孤立森林、Z-Score、统计学方法）
- **规则引擎**: 灵活的规则条件配置
- **通知服务**: 多渠道通知（Slack、邮件、Webhook）
- **指标查询**: Prometheus数据查询

### 3. 技术栈

- **框架**: FastAPI + Uvicorn
- **数据库**: SQLite（开发）/ PostgreSQL（生产）
- **缓存**: Redis
- **AI/ML**: Scikit-learn, Pandas, NumPy
- **监控**: Prometheus
- **测试**: Pytest