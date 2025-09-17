# 智能监控预警系统 - 数据库初始化和配置指南

本文档详细说明了如何配置、初始化和管理智能监控预警系统的数据库。

## 目录

1. [数据库架构](#数据库架构)
2. [数据库配置](#数据库配置)
3. [数据库初始化](#数据库初始化)
4. [数据库连接测试](#数据库连接测试)
5. [表结构说明](#表结构说明)
6. [数据初始化](#数据初始化)
7. [故障排除](#故障排除)

## 数据库架构

### 支持的数据库类型

项目支持两种数据库配置：
1. **开发环境**: SQLite（默认，用于本地开发）
2. **生产环境**: PostgreSQL（推荐，用于生产部署）

### 数据库设计原则

- 使用PostgreSQL作为主要数据库存储结构化数据
- 采用关系型数据模型设计
- 支持ACID事务特性
- 实现数据完整性和一致性约束

## 数据库配置

### 1. 环境变量配置

在 [.env](file:///d%3A/autocode/20250902/backend/.env) 文件中配置数据库连接信息：

```bash
# PostgreSQL数据库配置（生产环境）
DATABASE_URL=postgresql+asyncpg://postgres:zalando@192.168.233.133:30199/smart_monitoring

# SQLite数据库配置（开发环境，默认）
# DATABASE_URL=sqlite+aiosqlite:///./sql_app.db
```

### 2. 配置文件说明

核心配置在 [config.py](file:///d%3A/autocode/20250902/backend/app/core/config.py) 文件中定义：

```python
# 数据库配置
DATABASE_URL: str = Field(
    default="postgresql+asyncpg://postgres:zalando@192.168.233.133:30199/smart_monitoring", 
    env="DATABASE_URL"
)
```

### 3. 配置验证

创建配置验证脚本 [test_config.py](file:///d%3A/autocode/20250902/test_config.py)：

```python
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

运行验证：
```bash
python test_config.py
```

## 数据库初始化

### 1. 自动初始化

系统在启动时会自动初始化数据库表结构：

```python
# 在 main.py 中
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 初始化数据库
    await init_db()
```

### 2. 手动初始化

也可以手动执行数据库初始化：

```bash
# 初始化数据库表
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 3. 初始化脚本

数据库初始化逻辑在 [database.py](file:///d%3A/autocode/20250902/backend/app/core/database.py) 中实现：

```python
async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
```

## 数据库连接测试

### 1. 连接测试脚本

创建数据库连接测试脚本 [test_db_connection.py](file:///d%3A/autocode/20250902/backend/test_db_connection.py)：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能监控预警系统 - 数据库连接测试脚本
用于验证数据库连接和表结构
"""

import asyncio
import asyncpg
import os

# 数据库连接配置
DB_CONFIG = {
    'host': '192.168.233.133',
    'port': 30199,
    'user': 'postgres',
    'password': 'zalando',
    'database': 'smart_monitoring'
}

async def test_database_connection():
    """测试数据库连接"""
    try:
        # 连接到数据库
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✓ 数据库连接成功")
        
        # 测试查询用户表
        users = await conn.fetch("SELECT COUNT(*) as count FROM users")
        print(f"✓ 用户表记录数: {users[0]['count']}")
        
        # 测试查询巡检规则表
        rules = await conn.fetch("SELECT COUNT(*) as count FROM inspection_rules")
        print(f"✓ 巡检规则表记录数: {rules[0]['count']}")
        
        # 测试查询指标元数据表
        metrics = await conn.fetch("SELECT COUNT(*) as count FROM metrics_metadata")
        print(f"✓ 指标元数据表记录数: {metrics[0]['count']}")
        
        # 显示表结构信息
        print("\n数据库表结构信息:")
        tables = await conn.fetch("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        for table in tables:
            print(f"  - {table['table_name']} ({table['column_count']} 列)")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("智能监控预警系统 - 数据库连接测试")
    print("=" * 40)
    print(f"数据库地址: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"数据库名称: {DB_CONFIG['database']}")
    print("=" * 40)
    
    if await test_database_connection():
        print("\n✓ 所有数据库测试通过")
    else:
        print("\n✗ 数据库测试失败")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. 运行连接测试

```bash
cd backend
python test_db_connection.py
```

## 表结构说明

### 1. 用户表 (users)

存储系统用户信息：

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 巡检规则表 (inspection_rules)

存储巡检规则配置：

```sql
CREATE TABLE inspection_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    metric_name VARCHAR(100) NOT NULL,
    condition_type VARCHAR(20) NOT NULL,
    threshold_value DOUBLE PRECISION,
    severity VARCHAR(20) DEFAULT 'medium',
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. 指标数据表 (metrics_data)

存储监控指标数据：

```sql
CREATE TABLE metrics_data (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. 异常检测结果表 (anomaly_detection_results)

存储AI异常检测结果：

```sql
CREATE TABLE anomaly_detection_results (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    anomaly_score DOUBLE PRECISION,
    is_anomaly BOOLEAN DEFAULT false,
    algorithm VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. 通知记录表 (notification_logs)

存储通知发送记录：

```sql
CREATE TABLE notification_logs (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER,
    alert_message TEXT,
    channel VARCHAR(50),
    status VARCHAR(20),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);
```

## 数据初始化

### 1. 初始化脚本

创建数据库表和初始数据的脚本 [init_database.py](file:///d%3A/autocode/20250902/scripts/init_database.py)：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能监控预警系统 - 数据库初始化脚本
创建表结构并插入初始数据
"""

import asyncio
import asyncpg
import hashlib

# 数据库连接配置
DB_CONFIG = {
    'host': '192.168.233.133',
    'port': 30199,
    'user': 'postgres',
    'password': 'zalando',
    'database': 'smart_monitoring'
}

# 创建表的SQL语句
CREATE_TABLES_SQL = """
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 巡检规则表
CREATE TABLE IF NOT EXISTS inspection_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    metric_name VARCHAR(100) NOT NULL,
    condition_type VARCHAR(20) NOT NULL,
    threshold_value DOUBLE PRECISION,
    severity VARCHAR(20) DEFAULT 'medium',
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 指标数据表
CREATE TABLE IF NOT EXISTS metrics_data (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 异常检测结果表
CREATE TABLE IF NOT EXISTS anomaly_detection_results (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    anomaly_score DOUBLE PRECISION,
    is_anomaly BOOLEAN DEFAULT false,
    algorithm VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 通知记录表
CREATE TABLE IF NOT EXISTS notification_logs (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER,
    alert_message TEXT,
    channel VARCHAR(50),
    status VARCHAR(20),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);
"""

# 初始数据
INITIAL_DATA_SQL = """
-- 插入管理员用户 (密码: admin123)
INSERT INTO users (username, email, password_hash, role) VALUES 
('admin', 'admin@smart-monitoring.com', '{}', 'admin')
ON CONFLICT (username) DO NOTHING;

-- 插入示例巡检规则
INSERT INTO inspection_rules (name, description, metric_name, condition_type, threshold_value, severity) VALUES 
('CPU使用率监控', '监控CPU使用率超过阈值的情况', 'cpu_usage', 'greater_than', 80.0, 'high'),
('内存使用率监控', '监控内存使用率超过阈值的情况', 'memory_usage', 'greater_than', 85.0, 'medium'),
('磁盘空间监控', '监控磁盘使用率超过阈值的情况', 'disk_usage', 'greater_than', 90.0, 'high')
ON CONFLICT DO NOTHING;
""".format(hashlib.sha256("admin123".encode()).hexdigest())

async def init_database():
    """初始化数据库"""
    try:
        # 连接到数据库
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✓ 数据库连接成功")
        
        # 创建表
        await conn.execute(CREATE_TABLES_SQL)
        print("✓ 数据库表创建完成")
        
        # 插入初始数据
        await conn.execute(INITIAL_DATA_SQL)
        print("✓ 初始数据插入完成")
        
        # 验证表结构
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN 
            ('users', 'inspection_rules', 'metrics_data', 'anomaly_detection_results', 'notification_logs')
            ORDER BY table_name
        """)
        
        print(f"\n✓ 创建的表:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        await conn.close()
        print("\n✓ 数据库初始化完成")
        return True
        
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("智能监控预警系统 - 数据库初始化")
    print("=" * 40)
    print(f"数据库地址: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"数据库名称: {DB_CONFIG['database']}")
    print("=" * 40)
    
    if await init_database():
        print("\n🎉 数据库初始化成功完成")
    else:
        print("\n❌ 数据库初始化失败")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. 运行初始化脚本

```bash
cd scripts
python init_database.py
```

## 故障排除

### 1. 常见问题

#### 数据库连接失败

检查以下配置：
1. 数据库服务是否运行
2. 网络连接是否正常
3. 用户名和密码是否正确
4. 数据库名称是否存在

```bash
# 测试数据库连接
python test_db_connection.py
```

#### 表结构创建失败

检查SQL语法和权限：
```bash
# 手动执行SQL检查
psql -h 192.168.233.133 -p 30199 -U postgres -d smart_monitoring
```

#### 数据初始化失败

检查初始数据格式和约束：
```bash
# 查看表结构
\d table_name
```

### 2. 调试技巧

#### 启用详细日志

在 [.env](file:///d%3A/autocode/20250902/backend/.env) 文件中设置：
```bash
LOG_LEVEL=DEBUG
```

#### 查看数据库日志

```bash
# 查看PostgreSQL日志
tail -f /var/log/postgresql/postgresql-*.log
```

### 3. 性能优化

#### 连接池配置

在 [config.py](file:///d%3A/autocode/20250902/backend/app/core/config.py) 中配置连接池：
```python
# 数据库连接池配置
MAX_CONNECTIONS=100
CONNECTION_TIMEOUT=30
```

#### 索引优化

为常用查询字段创建索引：
```sql
-- 为时间戳字段创建索引
CREATE INDEX idx_metrics_timestamp ON metrics_data(timestamp);
CREATE INDEX idx_anomaly_timestamp ON anomaly_detection_results(timestamp);
```