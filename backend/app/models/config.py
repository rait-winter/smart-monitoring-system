#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置数据模型

定义系统配置的数据库模型，支持配置的持久化存储
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    config_type = Column(String(50), nullable=False, index=True, comment="配置类型")
    config_key = Column(String(100), nullable=False, index=True, comment="配置键")
    config_value = Column(JSON, nullable=True, comment="配置值")
    description = Column(Text, nullable=True, comment="配置描述")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<SystemConfig(id={self.id}, type={self.config_type}, key={self.config_key})>"


class PrometheusConfig(Base):
    """Prometheus配置表"""
    __tablename__ = "prometheus_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="配置名称")
    url = Column(String(500), nullable=False, comment="Prometheus服务器地址")
    username = Column(String(100), nullable=True, comment="用户名")
    password = Column(String(200), nullable=True, comment="密码")
    timeout = Column(Integer, default=30, comment="请求超时时间(秒)")
    scrape_interval = Column(String(20), default="15s", comment="采集间隔")
    evaluation_interval = Column(String(20), default="15s", comment="评估间隔")
    max_retries = Column(Integer, default=3, comment="最大重试次数")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    is_default = Column(Boolean, default=False, comment="是否为默认配置")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<PrometheusConfig(id={self.id}, name={self.name}, url={self.url})>"


class AIConfig(Base):
    """AI配置表"""
    __tablename__ = "ai_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="配置名称")
    model_path = Column(String(500), nullable=False, comment="模型路径")
    batch_size = Column(Integer, default=1000, comment="批处理大小")
    max_workers = Column(Integer, default=4, comment="最大工作线程数")
    algorithm_type = Column(String(50), default="isolation_forest", comment="算法类型")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    is_default = Column(Boolean, default=False, comment="是否为默认配置")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<AIConfig(id={self.id}, name={self.name}, model_path={self.model_path})>"
