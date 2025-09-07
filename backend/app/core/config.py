#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能监控预警系统 - 核心配置模块
高级配置管理，支持多环境动态配置
"""

import os
import secrets
from functools import lru_cache
from typing import List, Optional, Any, Dict
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """
    应用核心配置类
    
    使用Pydantic Settings进行环境变量管理和验证
    支持多环境配置，自动类型转换和验证
    
    配置优先级：
    1. 环境变量
    2. .env文件
    3. 默认值
    
    示例:
        # 从环境变量或.env文件读取
        settings = Settings()
        
        # 手动设置（主要用于测试）
        settings = Settings(DEBUG=True, SECRET_KEY="test-key")
    """
    
    # ===== 基础应用配置 =====
    APP_NAME: str = Field(default="智能监控预警系统", env="APP_NAME")
    APP_VERSION: str = Field(default="2.0.0", env="APP_VERSION") 
    APP_DESCRIPTION: str = Field(default="基于AI的自动化巡检与智能预警系统", env="APP_DESCRIPTION")
    
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    API_V1_PREFIX: str = Field(default="/api/v1", env="API_V1_PREFIX")
    
    # ===== 服务器配置 =====
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    RELOAD: bool = Field(default=False, env="RELOAD")
    
    # ===== 安全配置 =====
    SECRET_KEY: str = Field(env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    
    # ===== 跨域配置 =====
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="BACKEND_CORS_ORIGINS"
    )
    
    # ===== 数据库配置 =====
    POSTGRES_SERVER: str = Field(env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(env="POSTGRES_USER") 
    POSTGRES_PASSWORD: str = Field(env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(env="POSTGRES_DB")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # ===== Redis配置 =====
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_URL: Optional[RedisDsn] = None
    
    # ===== Prometheus配置 =====
    PROMETHEUS_URL: AnyHttpUrl = Field(default="http://localhost:9090", env="PROMETHEUS_URL")
    PROMETHEUS_TIMEOUT: int = Field(default=30, env="PROMETHEUS_TIMEOUT")
    PROMETHEUS_MAX_RETRIES: int = Field(default=3, env="PROMETHEUS_MAX_RETRIES")
    
    # ===== AI/ML配置 =====
    AI_MODEL_PATH: Path = Field(default=Path("./models"), env="AI_MODEL_PATH")
    AI_BATCH_SIZE: int = Field(default=1000, env="AI_BATCH_SIZE")
    AI_CACHE_TTL: int = Field(default=300, env="AI_CACHE_TTL")  # 5分钟
    AI_MAX_WORKERS: int = Field(default=2, env="AI_MAX_WORKERS")
    
    # ===== 通知服务配置 =====
    # Slack配置
    SLACK_WEBHOOK_URL: Optional[AnyHttpUrl] = Field(default=None, env="SLACK_WEBHOOK_URL")
    SLACK_BOT_TOKEN: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
    SLACK_CHANNEL: str = Field(default="#monitoring", env="SLACK_CHANNEL")
    
    # 邮件配置
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    
    # ===== 规则引擎配置 =====
    RULES_CHECK_INTERVAL: int = Field(default=60, env="RULES_CHECK_INTERVAL")  # 秒
    MAX_ALERT_FREQUENCY: int = Field(default=300, env="MAX_ALERT_FREQUENCY")   # 5分钟
    RULE_EXECUTION_TIMEOUT: int = Field(default=30, env="RULE_EXECUTION_TIMEOUT") # 30秒
    
    # ===== 性能配置 =====
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")  # 缓存TTL
    MAX_CONNECTIONS: int = Field(default=100, env="MAX_CONNECTIONS")
    CONNECTION_TIMEOUT: int = Field(default=30, env="CONNECTION_TIMEOUT")
    
    # ===== 日志配置 =====
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")  # json 或 text
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # ===== Sentry配置 =====
    SENTRY_DSN: Optional[AnyHttpUrl] = Field(default=None, env="SENTRY_DSN")
    
    # ===== 测试配置 =====
    TESTING: bool = Field(default=False, env="TESTING")
    TEST_DATABASE_URL: Optional[str] = Field(default=None, env="TEST_DATABASE_URL")
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: Optional[str]) -> str:
        """
        验证并生成SECRET_KEY
        
        如果未提供或长度不足，自动生成安全密钥
        生产环境中应显式设置此值
        
        Args:
            v: 输入的SECRET_KEY值
            
        Returns:
            str: 验证后的SECRET_KEY
            
        Raises:
            ValueError: 当生产环境中SECRET_KEY为空时
        """
        if v is None or len(v) < 32:
            # 在生产环境中不应自动生成，而应要求显式设置
            if os.getenv('ENVIRONMENT', '').lower() == 'production':
                raise ValueError('生产环境中必须设置安全的SECRET_KEY')
            return secrets.token_urlsafe(32)
        return v
    
    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    @classmethod
    def assemble_cors_origins(cls, v):
        """
        解析CORS origins配置
        
        支持多种格式输入：
        - 字符串: "http://localhost:3000,http://localhost:8080"
        - 列表: ["http://localhost:3000", "http://localhost:8080"]
        
        Args:
            v: 输入的CORS origins值
            
        Returns:
            List[str]: 解析后的origins列表
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(f"无效的CORS origins格式: {v}")
    
    @model_validator(mode='before')
    @classmethod
    def assemble_database_url(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建数据库连接URL
        
        从单独的数据库配置参数构建PostgreSQL连接字符串
        支持异步连接(asyncpg)和同步连接(psycopg2)
        
        Args:
            values: 配置字典
            
        Returns:
            Dict[str, Any]: 更新后的配置字典
        """
        if "DATABASE_URL" in values and values["DATABASE_URL"]:
            return values
        
        # 构建PostgreSQL URL
        try:
            postgres_url = PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=values.get("POSTGRES_SERVER"),
                port=values.get("POSTGRES_PORT", 5432),
                path=values.get('POSTGRES_DB', ''),
            )
            values["DATABASE_URL"] = str(postgres_url)
        except Exception as e:
            # 如果构建失败，使用默认格式
            user = values.get("POSTGRES_USER", "monitoring")
            password = values.get("POSTGRES_PASSWORD", "monitoring123")
            host = values.get("POSTGRES_SERVER", "localhost")
            port = values.get("POSTGRES_PORT", 5432)
            db = values.get("POSTGRES_DB", "smart_monitoring")
            values["DATABASE_URL"] = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
        
        return values
    
    @model_validator(mode='before')
    @classmethod  
    def assemble_redis_url(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建Redis连接URL
        
        从单独的Redis配置参数构建Redis连接字符串
        支持密码认证和数据库选择
        
        Args:
            values: 配置字典
            
        Returns:
            Dict[str, Any]: 更新后的配置字典
        """
        if "REDIS_URL" in values and values["REDIS_URL"]:
            return values
        
        # 构建Redis URL
        try:
            redis_url = RedisDsn.build(
                scheme="redis",
                password=values.get("REDIS_PASSWORD"),
                host=values.get("REDIS_HOST", "localhost"),
                port=values.get("REDIS_PORT", 6379),
                path=str(values.get("REDIS_DB", 0)),
            )
            values["REDIS_URL"] = str(redis_url)
        except Exception as e:
            # 如果构建失败，使用默认格式
            host = values.get("REDIS_HOST", "localhost")
            port = values.get("REDIS_PORT", 6379)
            password = values.get("REDIS_PASSWORD")
            db = values.get("REDIS_DB", 0)
            
            if password:
                values["REDIS_URL"] = f"redis://:{password}@{host}:{port}/{db}"
            else:
                values["REDIS_URL"] = f"redis://{host}:{port}/{db}"
        
        return values
    
    @field_validator("AI_MODEL_PATH", mode='before')
    @classmethod
    def validate_model_path(cls, v) -> Path:
        """
        验证AI模型路径
        
        确保模型目录存在，如果不存在则自动创建
        支持相对路径和绝对路径
        
        Args:
            v: 输入的路径值
            
        Returns:
            Path: 验证后的Path对象
        """
        path = Path(v)
        try:
            path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # 如果没有权限创建，警告但不阻止运行
            import warnings
            warnings.warn(f"无法创建模型目录: {path}")
        return path
    
    @property
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_url_sync(self) -> str:
        """同步数据库URL（用于Alembic）"""
        return str(self.DATABASE_URL).replace("+asyncpg", "")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",  # 忽略未定义的字段
    }


@lru_cache()
def get_settings() -> Settings:
    """获取应用设置（带缓存）"""
    return Settings()


# 创建全局设置实例
settings = get_settings()