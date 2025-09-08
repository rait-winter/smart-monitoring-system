#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接管理模块

使用SQLAlchemy 2.0异步引擎与连接池优化
支持异步操作、连接池管理、事务处理等功能

主要功能:
- 异步数据库引擎创建和管理
- 会话工厂和依赖注入
- 数据库初始化和清理
- 连接健康检查
- 事务管理

使用示例:
    # 获取数据库会话
    async with get_async_session() as session:
        # 执行数据库操作
        result = await session.execute(select(User))
        users = result.scalars().all()
        
    # 或者使用依赖注入（在FastAPI路由中）
    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_async_session)):
        result = await db.execute(select(User))
        return result.scalars().all()
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import NullPool
from sqlalchemy import MetaData, event
from sqlalchemy.engine import Engine
import structlog

from app.core.config import settings

# 配置日志
logger = structlog.get_logger(__name__)

# 数据库元数据配置
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)


class Base(DeclarativeBase):
    """数据库模型基类"""
    metadata = metadata
    
    # 通用字段类型注解
    type_annotation_map = {
        str: mapped_column(nullable=False),
    }


# 创建异步引擎
def create_engine():
    """创建数据库引擎"""
    engine_kwargs = {
        "echo": settings.DEBUG,
        "echo_pool": settings.DEBUG,
        "pool_pre_ping": True,
        "pool_recycle": 3600,  # 1小时回收连接
    }
    
    # 根据数据库类型设置连接池参数
    database_url = str(settings.DATABASE_URL)
    if "sqlite" in database_url:
        # SQLite不需要连接池参数
        engine_kwargs["poolclass"] = NullPool
        # 移除不适用于SQLite的参数
        engine_kwargs.pop("pool_recycle", None)
    else:
        # PostgreSQL等数据库使用连接池
        engine_kwargs["max_overflow"] = 20
        engine_kwargs["pool_size"] = 10
    
    # 测试环境使用NullPool
    if settings.TESTING:
        engine_kwargs["poolclass"] = NullPool
        # 移除不适用于NullPool的参数
        engine_kwargs.pop("max_overflow", None)
        engine_kwargs.pop("pool_size", None)
        engine_kwargs.pop("pool_recycle", None)
    
    return create_async_engine(database_url, **engine_kwargs)


# 创建引擎实例
engine = create_engine()

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


# SQLite外键约束支持（如果使用SQLite）
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """为SQLite启用外键约束"""
    if "sqlite" in str(settings.DATABASE_URL):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def get_async_session() -> AsyncSession:
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error("数据库会话错误", error=str(e), exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表初始化完成")


async def drop_db():
    """删除所有数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("数据库表删除完成")


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
    logger.info("数据库连接已关闭")