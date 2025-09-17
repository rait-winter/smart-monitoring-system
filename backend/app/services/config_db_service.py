#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置数据库服务

提供配置的数据库存储和管理功能
支持Prometheus、AI等各类配置的CRUD操作
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import structlog

from app.core.database import get_db_session
from app.models.config import SystemConfig, PrometheusConfig, AIConfig

logger = structlog.get_logger(__name__)


class ConfigDBService:
    """配置数据库服务"""
    
    async def get_prometheus_configs(self) -> List[Dict[str, Any]]:
        """获取所有Prometheus配置"""
        async with get_db_session() as db:
            result = await db.execute(
                select(PrometheusConfig).where(PrometheusConfig.is_enabled == True)
            )
            configs = result.scalars().all()
            return [
                {
                    "id": config.id,
                    "name": config.name,
                    "url": config.url,
                    "username": config.username,
                    "password": config.password,
                    "timeout": config.timeout,
                    "scrape_interval": config.scrape_interval,
                    "evaluation_interval": config.evaluation_interval,
                    "max_retries": config.max_retries,
                    "is_enabled": config.is_enabled,
                    "is_default": config.is_default,
                    "created_at": config.created_at.isoformat() if config.created_at else None,
                    "updated_at": config.updated_at.isoformat() if config.updated_at else None
                }
                for config in configs
            ]
    
    async def get_default_prometheus_config(self) -> Optional[Dict[str, Any]]:
        """获取默认Prometheus配置"""
        async with get_db_session() as db:
            result = await db.execute(
                select(PrometheusConfig).where(PrometheusConfig.is_default == True)
            )
            config = result.scalar_one_or_none()
            if config:
                return {
                    "id": config.id,
                    "name": config.name,
                    "url": config.url,
                    "username": config.username,
                    "password": config.password,
                    "timeout": config.timeout,
                    "scrape_interval": config.scrape_interval,
                    "evaluation_interval": config.evaluation_interval,
                    "max_retries": config.max_retries,
                    "is_enabled": config.is_enabled,
                    "is_default": config.is_default
                }
            return None
    
    async def save_prometheus_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存Prometheus配置"""
        async with get_db_session() as db:
            # 检查是否已存在默认配置
            existing_config = await self.get_default_prometheus_config()
            
            if existing_config:
                # 更新现有配置
                await db.execute(
                    update(PrometheusConfig)
                    .where(PrometheusConfig.is_default == True)
                    .values(
                        name=config_data.get("name", "默认配置"),
                        url=config_data.get("url", ""),
                        username=config_data.get("username"),
                        password=config_data.get("password"),
                        timeout=config_data.get("timeout", 30),
                        scrape_interval=config_data.get("scrapeInterval", config_data.get("scrape_interval", "15s")),
                        evaluation_interval=config_data.get("evaluationInterval", config_data.get("evaluation_interval", "15s")),
                        max_retries=config_data.get("max_retries", 3),
                        is_enabled=config_data.get("enabled", True)
                    )
                )
                config_id = existing_config["id"]
            else:
                # 创建新配置
                new_config = PrometheusConfig(
                    name=config_data.get("name", "默认配置"),
                    url=config_data.get("url", ""),
                    username=config_data.get("username"),
                    password=config_data.get("password"),
                    timeout=config_data.get("timeout", 30),
                    scrape_interval=config_data.get("scrapeInterval", config_data.get("scrape_interval", "15s")),
                    evaluation_interval=config_data.get("evaluationInterval", config_data.get("evaluation_interval", "15s")),
                    max_retries=config_data.get("max_retries", 3),
                    is_enabled=config_data.get("enabled", True),
                    is_default=True
                )
                db.add(new_config)
                await db.flush()
                config_id = new_config.id
            
            await db.commit()
            logger.info("Prometheus配置保存成功", config_id=config_id, config_data=config_data)
            
            return {
                "id": config_id,
                "message": "配置保存成功",
                "config": config_data
            }
    
    async def get_ai_configs(self) -> List[Dict[str, Any]]:
        """获取所有AI配置"""
        async with get_db_session() as db:
            result = await db.execute(
                select(AIConfig).where(AIConfig.is_enabled == True)
            )
            configs = result.scalars().all()
            return [
                {
                    "id": config.id,
                    "name": config.name,
                    "model_path": config.model_path,
                    "batch_size": config.batch_size,
                    "max_workers": config.max_workers,
                    "algorithm_type": config.algorithm_type,
                    "is_enabled": config.is_enabled,
                    "is_default": config.is_default,
                    "created_at": config.created_at.isoformat() if config.created_at else None,
                    "updated_at": config.updated_at.isoformat() if config.updated_at else None
                }
                for config in configs
            ]
    
    async def save_ai_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存AI配置"""
        async with get_db_session() as db:
            # 检查是否已存在默认配置
            result = await db.execute(
                select(AIConfig).where(AIConfig.is_default == True)
            )
            existing_config = result.scalar_one_or_none()
            
            if existing_config:
                # 更新现有配置
                await db.execute(
                    update(AIConfig)
                    .where(AIConfig.is_default == True)
                    .values(
                        name=config_data.get("name", "默认AI配置"),
                        model_path=config_data.get("model_path", "./models"),
                        batch_size=config_data.get("batch_size", 1000),
                        max_workers=config_data.get("max_workers", 4),
                        algorithm_type=config_data.get("algorithm_type", "isolation_forest"),
                        is_enabled=config_data.get("enabled", True)
                    )
                )
                config_id = existing_config.id
            else:
                # 创建新配置
                new_config = AIConfig(
                    name=config_data.get("name", "默认AI配置"),
                    model_path=config_data.get("model_path", "./models"),
                    batch_size=config_data.get("batch_size", 1000),
                    max_workers=config_data.get("max_workers", 4),
                    algorithm_type=config_data.get("algorithm_type", "isolation_forest"),
                    is_enabled=config_data.get("enabled", True),
                    is_default=True
                )
                db.add(new_config)
                await db.flush()
                config_id = new_config.id
            
            await db.commit()
            logger.info("AI配置保存成功", config_id=config_id, config_data=config_data)
            
            return {
                "id": config_id,
                "message": "AI配置保存成功",
                "config": config_data
            }


# 全局配置数据库服务实例
config_db_service = ConfigDBService()
