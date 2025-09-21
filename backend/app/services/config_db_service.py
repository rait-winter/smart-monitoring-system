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

from app.core.database import AsyncSessionLocal
from app.models.config import SystemConfig, PrometheusConfig, OllamaConfig, DatabaseConfig, AIConfig

logger = structlog.get_logger(__name__)


class ConfigDBService:
    """配置数据库服务"""
    
    async def get_prometheus_configs(self) -> List[Dict[str, Any]]:
        """获取所有Prometheus配置"""
        async with AsyncSessionLocal() as db:
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
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(PrometheusConfig).where(PrometheusConfig.is_default == True)
            )
            config = result.scalar_one_or_none()
            if config:
                # 处理名称显示问题
                config_name = config.name
                if not config_name or config_name.strip() == "" or "?" in config_name:
                    config_name = "默认Prometheus配置"
                
                return {
                    "id": config.id,
                    "name": config_name,
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
    
    def validate_config_name(self, name: str) -> Dict[str, Any]:
        """验证配置名称"""
        if not name or not name.strip():
            return {"valid": False, "message": "配置名称不能为空"}
        
        name = name.strip()
        
        # 只允许字母、数字、下划线、短横线
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return {"valid": False, "message": "配置名称只能包含字母、数字、下划线(_)和短横线(-)"}
        
        # 长度限制
        if len(name) < 2:
            return {"valid": False, "message": "配置名称至少需要2个字符"}
        
        if len(name) > 50:
            return {"valid": False, "message": "配置名称不能超过50个字符"}
        
        # 不能以数字开头
        if re.match(r'^[0-9]', name):
            return {"valid": False, "message": "配置名称不能以数字开头"}
        
        # 不能以特殊符号开头或结尾
        if re.match(r'^[-_]|[-_]$', name):
            return {"valid": False, "message": "配置名称不能以下划线或短横线开头/结尾"}
        
        return {"valid": True}

    async def save_prometheus_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存Prometheus配置"""
        try:
            logger.info("🔍 接收到的配置数据", config_data=config_data)
            
            # 验证配置名称
            name = config_data.get("name", "").strip()
            logger.info("🔍 提取的配置名称", name=name, raw_name=config_data.get("name"))
            
            if not name:
                return {"success": False, "message": "配置名称不能为空"}
            
            name_validation = self.validate_config_name(name)
            if not name_validation["valid"]:
                return {"success": False, "message": name_validation["message"]}
            
            # 使用引擎直接创建写事务
            from app.core.database import engine
            async with engine.begin() as conn:
                try:
                    
                    # 检查是否已存在同名配置
                    result = await conn.execute(
                        select(PrometheusConfig.id).where(PrometheusConfig.name == name)
                    )
                    existing_config_id = result.scalar_one_or_none()
                    
                    if existing_config_id:
                        # 更新现有同名配置
                        await conn.execute(
                            update(PrometheusConfig)
                            .where(PrometheusConfig.id == existing_config_id)
                            .values(
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
                        config_id = existing_config_id
                        logger.info("更新现有配置", config_name=name, config_id=config_id)
                    else:
                        # 检查是否需要设置为默认配置（如果没有其他默认配置）
                        default_result = await conn.execute(
                            select(PrometheusConfig.id).where(PrometheusConfig.is_default == True)
                        )
                        has_default = default_result.scalar_one_or_none() is not None
                        
                        # 插入新配置
                        insert_result = await conn.execute(
                            PrometheusConfig.__table__.insert().values(
                                name=name,
                                url=config_data.get("url", ""),
                                username=config_data.get("username"),
                                password=config_data.get("password"),
                                timeout=config_data.get("timeout", 30),
                                scrape_interval=config_data.get("scrapeInterval", config_data.get("scrape_interval", "15s")),
                                evaluation_interval=config_data.get("evaluationInterval", config_data.get("evaluation_interval", "15s")),
                                max_retries=config_data.get("max_retries", 3),
                                is_enabled=config_data.get("enabled", True),
                                is_default=not has_default  # 如果没有默认配置，则设为默认
                            ).returning(PrometheusConfig.id)
                        )
                        config_id = insert_result.scalar()
                        logger.info("创建新配置", config_name=name, config_id=config_id, is_default=not has_default)
                    
                    logger.info("Prometheus配置保存成功", config_id=config_id, config_data=config_data)
                except Exception as e:
                    logger.error("保存配置时出错", error=str(e))
                    raise e
                
                return {
                    "success": True,
                    "id": config_id,
                    "message": "配置保存成功",
                    "config": config_data
                }
                
        except Exception as e:
            logger.error("保存Prometheus配置失败", error=str(e))
            return {
                "success": False,
                "message": f"配置保存失败: {str(e)}"
            }
    
    async def set_current_prometheus_config(self, config_id: int) -> Dict[str, Any]:
        """设置当前使用的Prometheus配置"""
        logger.info("开始设置当前配置", config_id=config_id)
        
        try:
            from app.core.database import engine
            logger.info("创建数据库连接")
            
            async with engine.begin() as conn:
                logger.info("开始数据库事务")
                
                # 首先清除所有配置的默认状态
                logger.info("清除所有默认状态")
                await conn.execute(
                    update(PrometheusConfig).values(is_default=False)
                )
                
                # 设置指定配置为默认
                logger.info("设置指定配置为默认", config_id=config_id)
                result = await conn.execute(
                    update(PrometheusConfig)
                    .where(PrometheusConfig.id == config_id)
                    .values(is_default=True)
                )
                
                logger.info("更新结果", rowcount=result.rowcount)
                
                if result.rowcount == 0:
                    logger.warning("配置不存在", config_id=config_id)
                    return {
                        "success": False,
                        "message": "指定的配置不存在"
                    }
                
                logger.info("设置当前配置成功", config_id=config_id)
                success_result = {
                    "success": True,
                    "message": "当前配置设置成功"
                }
                logger.info("准备返回成功结果", result=success_result)
                return success_result
                
        except Exception as e:
            logger.error("设置当前配置失败", error=str(e))
            error_result = {
                "success": False,
                "message": f"设置当前配置失败: {str(e)}"
            }
            logger.info("准备返回错误结果", result=error_result)
            return error_result
    
    async def get_ai_configs(self) -> List[Dict[str, Any]]:
        """获取所有AI配置"""
        async with AsyncSessionLocal() as db:
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
        async with AsyncSessionLocal() as db:
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

    async def get_all_prometheus_configs(self):
        """获取所有Prometheus配置"""
        try:
            db = AsyncSessionLocal()
            result = await db.execute(
                select(PrometheusConfig).order_by(PrometheusConfig.created_at.desc())
            )
            configs = result.scalars().all()  # 使用 scalars().all() 获取模型对象
            
            config_list = []
            for config in configs:
                # 处理名称显示问题，如果名称为空或异常，使用默认值
                config_name = config.name
                if not config_name or config_name.strip() == "" or "?" in config_name:
                    config_name = "默认Prometheus配置"
                
                config_dict = {
                    "id": config.id,
                    "name": config_name,
                    "url": config.url,
                    "username": config.username,
                    "password": "***" if config.password else None,  # 隐藏密码
                    "timeout": config.timeout,
                    "scrape_interval": config.scrape_interval,
                    "evaluation_interval": config.evaluation_interval,
                    "max_retries": config.max_retries,
                    "is_enabled": config.is_enabled,
                    "is_default": config.is_default,
                    "is_current": config.is_default,  # 当前使用的配置
                    "connection_status": "unknown",  # 可以后续实现连接状态检查
                    "created_at": config.created_at.isoformat() if config.created_at else None,
                    "updated_at": config.updated_at.isoformat() if config.updated_at else None
                }
                config_list.append(config_dict)
            
            await db.close()
            return config_list
            
        except Exception as e:
            logger.error("获取所有配置失败", error=str(e))
            raise

    async def get_prometheus_config_by_id(self, config_id: int):
        """根据ID获取Prometheus配置"""
        try:
            db = AsyncSessionLocal()
            result = await db.execute(
                select(PrometheusConfig).where(PrometheusConfig.id == config_id)
            )
            config = result.scalars().first()  # 使用 scalars().first() 获取模型对象
            
            if config:
                config_dict = {
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
                    "is_current": config.is_default,
                    "created_at": config.created_at.isoformat() if config.created_at else None,
                    "updated_at": config.updated_at.isoformat() if config.updated_at else None
                }
                await db.close()
                return config_dict
            
            await db.close()
            return None
            
        except Exception as e:
            logger.error("获取配置失败", error=str(e))
            raise


    async def delete_prometheus_config(self, config_id: int):
        """删除Prometheus配置"""
        try:
            db = AsyncSessionLocal()
            
            await db.execute(
                delete(PrometheusConfig).where(PrometheusConfig.id == config_id)
            )
            
            await db.commit()
            await db.close()
            
        except Exception as e:
            logger.error("删除配置失败", error=str(e))
            await db.rollback()
            raise

    async def clear_config_history(self):
        """清空配置历史（保留当前配置）"""
        try:
            db = AsyncSessionLocal()
            
            # 删除所有非默认配置
            await db.execute(
                delete(PrometheusConfig).where(PrometheusConfig.is_default == False)
            )
            
            await db.commit()
            await db.close()
            
        except Exception as e:
            logger.error("清空配置历史失败", error=str(e))
            await db.rollback()
            raise

    # ==================== Ollama配置管理 ====================
    
    async def save_ollama_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存Ollama配置到数据库"""
        try:
            logger.info("🔍 接收到的Ollama配置数据", config_data=config_data)
            
            # 提取配置名称
            raw_name = config_data.get("name", "")
            name = raw_name.strip() if raw_name else ""
            logger.info("🔍 提取的Ollama配置名称", name=name, raw_name=raw_name)
            
            if not name:
                return {"success": False, "message": "配置名称不能为空"}
            
            name_validation = self.validate_config_name(name)
            if not name_validation["valid"]:
                return {"success": False, "message": name_validation["message"]}
            
            # 使用引擎直接创建写事务
            from app.core.database import engine
            async with engine.begin() as conn:
                try:
                    # 检查是否已存在同名配置
                    result = await conn.execute(
                        select(OllamaConfig.id).where(OllamaConfig.name == name)
                    )
                    existing_config_id = result.scalar_one_or_none()
                    
                    if existing_config_id:
                        # 更新现有同名配置
                        await conn.execute(
                            update(OllamaConfig)
                            .where(OllamaConfig.id == existing_config_id)
                            .values(
                                api_url=config_data.get("apiUrl", "http://localhost:11434"),
                                model=config_data.get("model", "llama3.2"),
                                timeout=config_data.get("timeout", 60000),
                                max_tokens=config_data.get("maxTokens", 2048),
                                temperature=config_data.get("temperature", 0.7),
                                is_enabled=config_data.get("enabled", True)
                            )
                        )
                        config_id = existing_config_id
                        logger.info("更新现有Ollama配置", config_name=name, config_id=config_id)
                    else:
                        # 检查是否需要设置为默认配置（如果没有其他默认配置）
                        default_result = await conn.execute(
                            select(OllamaConfig.id).where(OllamaConfig.is_default == True)
                        )
                        has_default = default_result.scalar_one_or_none() is not None
                        
                        # 插入新配置
                        insert_result = await conn.execute(
                            OllamaConfig.__table__.insert().values(
                                name=name,
                                api_url=config_data.get("apiUrl", "http://localhost:11434"),
                                model=config_data.get("model", "llama3.2"),
                                timeout=config_data.get("timeout", 60000),
                                max_tokens=config_data.get("maxTokens", 2048),
                                temperature=config_data.get("temperature", 0.7),
                                is_enabled=config_data.get("enabled", True),
                                is_default=not has_default  # 如果没有默认配置，则设为默认
                            ).returning(OllamaConfig.id)
                        )
                        config_id = insert_result.scalar()
                        logger.info("创建新Ollama配置", config_name=name, config_id=config_id, is_default=not has_default)
                    
                    logger.info("Ollama配置保存成功", config_id=config_id, config_data=config_data)
                    
                    return {
                        "success": True,
                        "message": "配置保存成功",
                        "id": config_id,
                        "config": {
                            "name": name,
                            "apiUrl": config_data.get("apiUrl", "http://localhost:11434"),
                            "model": config_data.get("model", "llama3.2"),
                            "timeout": config_data.get("timeout", 60000),
                            "maxTokens": config_data.get("maxTokens", 2048),
                            "temperature": config_data.get("temperature", 0.7),
                            "enabled": config_data.get("enabled", True)
                        }
                    }
                except Exception as e:
                    logger.error("保存Ollama配置时出错", error=str(e))
                    raise e
                
        except Exception as e:
            logger.error("保存Ollama配置失败", error=str(e))
            return {
                "success": False,
                "message": f"配置保存失败: {str(e)}"
            }
    
    async def get_default_ollama_config(self) -> Dict[str, Any]:
        """获取默认Ollama配置"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(OllamaConfig).where(OllamaConfig.is_default == True)
                )
                config = result.scalar_one_or_none()
                
                if config:
                    # 确保配置名称存在且有效
                    name = config.name
                    if not name or name.strip() == "" or "?" in name:
                        name = "默认Ollama配置"
                    
                    return {
                        "name": name,
                        "enabled": config.is_enabled,
                        "apiUrl": config.api_url,
                        "model": config.model,
                        "timeout": config.timeout,
                        "maxTokens": config.max_tokens,
                        "temperature": config.temperature,
                        "id": config.id,
                        "updatedAt": config.updated_at.isoformat() if config.updated_at else None
                    }
                return None
        except Exception as e:
            logger.error("获取默认Ollama配置失败", error=str(e))
            return None
    
    async def get_all_ollama_configs(self) -> List[Dict[str, Any]]:
        """获取所有Ollama配置"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(OllamaConfig).order_by(OllamaConfig.updated_at.desc())
                )
                configs = result.scalars().all()
                
                config_list = []
                for config in configs:
                    # 确保配置名称存在且有效
                    name = config.name
                    if not name or name.strip() == "" or "?" in name:
                        name = f"配置{config.id}"
                    
                    config_list.append({
                        "id": config.id,
                        "name": name,
                        "apiUrl": config.api_url,
                        "model": config.model,
                        "timeout": config.timeout,
                        "maxTokens": config.max_tokens,
                        "temperature": config.temperature,
                        "enabled": config.is_enabled,
                        "isDefault": config.is_default,
                        "createdAt": config.created_at.isoformat() if config.created_at else None,
                        "updatedAt": config.updated_at.isoformat() if config.updated_at else None
                    })
                
                return config_list
        except Exception as e:
            logger.error("获取所有Ollama配置失败", error=str(e))
            return []
    
    async def set_current_ollama_config(self, config_id: int) -> Dict[str, Any]:
        """设置当前使用的Ollama配置"""
        logger.info("开始设置当前Ollama配置", config_id=config_id)
        
        try:
            from app.core.database import engine
            async with engine.begin() as conn:
                # 首先清除所有配置的默认状态
                await conn.execute(
                    update(OllamaConfig).values(is_default=False)
                )
                
                # 设置指定配置为默认
                result = await conn.execute(
                    update(OllamaConfig)
                    .where(OllamaConfig.id == config_id)
                    .values(is_default=True)
                )
                
                if result.rowcount == 0:
                    return {
                        "success": False,
                        "message": "指定的配置不存在"
                    }
                
                logger.info("设置当前Ollama配置成功", config_id=config_id)
                
                return {
                    "success": True,
                    "message": "当前配置设置成功"
                }
                
        except Exception as e:
            logger.error("设置当前Ollama配置失败", error=str(e))
            return {
                "success": False,
                "message": f"设置当前配置失败: {str(e)}"
            }

    # ==================== 数据库配置管理 ====================

    async def save_database_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存/更新数据库配置"""
        try:
            logger.info("保存数据库配置", config_data=config_data)
            
            # 提取配置数据
            name = config_data.get("name", "").strip()
            postgresql_config = config_data.get("postgresql", {})
            backup_config = config_data.get("backup", {})
            
            logger.debug("提取的配置名称", name=name)
            
            # 验证配置名称
            if not name:
                return {
                    "success": False,
                    "message": "配置名称不能为空"
                }
            
            validation_result = self.validate_config_name(name)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "message": validation_result["message"]
                }
            
            from app.core.database import engine
            async with engine.begin() as conn:
                db = AsyncSession(bind=conn)
                
                # 检查是否存在同名配置
                result = await db.execute(
                    select(DatabaseConfig.id).where(DatabaseConfig.name == name)
                )
                existing_config_id = result.scalar_one_or_none()
                
                config_dict = {
                    "name": name,
                    "host": postgresql_config.get("host", "localhost"),
                    "port": postgresql_config.get("port", 5432),
                    "database_name": postgresql_config.get("database", "monitoring"),
                    "username": postgresql_config.get("username", "postgres"),
                    "password": postgresql_config.get("password", ""),
                    "ssl_enabled": postgresql_config.get("ssl", False),
                    "connection_timeout": 30000,  # 固定值
                    "query_timeout": 60000,  # 固定值
                    "pool_size": 20,  # 固定值
                    "backup_enabled": backup_config.get("enabled", True),
                    "backup_schedule": backup_config.get("schedule", "0 2 * * *"),
                    "backup_retention": backup_config.get("retention", 30),
                    "backup_path": backup_config.get("path", "/data/backups"),
                    "is_enabled": postgresql_config.get("enabled", True),
                    "is_default": False  # 初始不设为默认
                }
                
                if existing_config_id:
                    # 更新现有配置
                    await db.execute(
                        update(DatabaseConfig)
                        .where(DatabaseConfig.id == existing_config_id)
                        .values(**config_dict)
                    )
                    config_id = existing_config_id
                    logger.info("更新数据库配置成功", config_id=config_id, name=name)
                else:
                    # 检查是否是第一个配置，如果是则设为默认
                    count_result = await db.execute(select(DatabaseConfig.id))
                    existing_configs = count_result.scalars().all()
                    
                    if not existing_configs:
                        config_dict["is_default"] = True
                        logger.info("设置为默认数据库配置", name=name)
                    
                    # 创建新配置
                    new_config = DatabaseConfig(**config_dict)
                    db.add(new_config)
                    await db.flush()
                    config_id = new_config.id
                    logger.info("创建数据库配置成功", config_id=config_id, name=name)
                
                return {
                    "success": True,
                    "message": "数据库配置保存成功",
                    "id": config_id,
                    "name": name
                }
                
        except Exception as e:
            logger.error("保存数据库配置失败", error=str(e), config_data=config_data)
            return {
                "success": False,
                "message": f"配置保存失败: {str(e)}"
            }

    async def get_default_database_config(self) -> Dict[str, Any]:
        """获取默认数据库配置"""
        try:
            async with AsyncSessionLocal() as db:
                # 首先尝试获取默认配置
                result = await db.execute(
                    select(DatabaseConfig).where(DatabaseConfig.is_default == True)
                )
                config = result.scalars().first()
                
                if not config:
                    # 如果没有默认配置，获取最新的一个
                    result = await db.execute(
                        select(DatabaseConfig).order_by(DatabaseConfig.updated_at.desc())
                    )
                    config = result.scalars().first()
                
                if config:
                    # 确保名称不为空或异常
                    config_name = config.name
                    if not config_name or config_name.strip() == "" or "?" in config_name:
                        config_name = "默认数据库配置"
                    
                    return {
                        "id": config.id,
                        "name": config_name,
                        "host": config.host,
                        "port": config.port,
                        "database": config.database_name,
                        "username": config.username,
                        "password": config.password,
                        "ssl": config.ssl_enabled,
                        "connectionTimeout": config.connection_timeout,
                        "queryTimeout": config.query_timeout,
                        "poolSize": config.pool_size,
                        "backupEnabled": config.backup_enabled,
                        "backupSchedule": config.backup_schedule,
                        "backupRetention": config.backup_retention,
                        "backupPath": config.backup_path,
                        "enabled": config.is_enabled,
                        "isDefault": config.is_default,
                        "updatedAt": config.updated_at.isoformat() if config.updated_at else None
                    }
                    
                return None
                
        except Exception as e:
            logger.error("获取默认数据库配置失败", error=str(e))
            # 如果数据库连接失败，尝试从环境变量获取配置
            import os
            database_url = os.environ.get('DATABASE_URL', '')
            if database_url and 'postgresql' in database_url:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(database_url)
                    logger.info("使用环境变量数据库配置", database_url=database_url)
                    return {
                        "id": 0,
                        "name": "环境变量配置",
                        "host": parsed.hostname or "localhost",
                        "port": parsed.port or 5432,
                        "database": parsed.path.lstrip('/') if parsed.path else "smart_monitoring",
                        "username": parsed.username or "postgres",
                        "password": parsed.password or "",
                        "ssl": 'sslmode=require' in database_url,
                        "connectionTimeout": 30000,
                        "queryTimeout": 60000,
                        "poolSize": 20,
                        "backupEnabled": False,
                        "backupSchedule": "0 2 * * *",
                        "backupRetention": 30,
                        "backupPath": "/data/backups",
                        "enabled": True,
                        "isDefault": True,
                        "updatedAt": None
                    }
                except Exception as parse_error:
                    logger.error("解析DATABASE_URL失败", error=str(parse_error))
            
            return None

    async def get_all_database_configs(self) -> List[Dict[str, Any]]:
        """获取所有数据库配置"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(DatabaseConfig).order_by(DatabaseConfig.updated_at.desc())
                )
                configs = result.scalars().all()
                
                config_list = []
                for config in configs:
                    # 确保名称不为空或异常
                    config_name = config.name
                    if not config_name or config_name.strip() == "" or "?" in config_name:
                        config_name = f"数据库配置_{config.id}"
                    
                    config_list.append({
                        "id": config.id,
                        "name": config_name,
                        "host": config.host,
                        "port": config.port,
                        "database": config.database_name,
                        "username": config.username,
                        "ssl": config.ssl_enabled,
                        "enabled": config.is_enabled,
                        "isDefault": config.is_default,
                        "updatedAt": config.updated_at.isoformat() if config.updated_at else None,
                        "createdAt": config.created_at.isoformat() if config.created_at else None
                    })
                
                logger.info("获取数据库配置列表成功", count=len(config_list))
                return config_list
                
        except Exception as e:
            logger.error("获取数据库配置列表失败", error=str(e))
            # 如果数据库连接失败，尝试从环境变量返回配置
            import os
            database_url = os.environ.get('DATABASE_URL', '')
            if database_url and 'postgresql' in database_url:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(database_url)
                    return [{
                        "id": 0,
                        "name": "环境变量配置",
                        "host": parsed.hostname or "localhost",
                        "port": parsed.port or 5432,
                        "database": parsed.path.lstrip('/') if parsed.path else "smart_monitoring",
                        "username": parsed.username or "postgres",
                        "ssl": 'sslmode=require' in database_url,
                        "enabled": True,
                        "isDefault": True,
                        "updatedAt": None,
                        "createdAt": None
                    }]
                except Exception:
                    pass
            return []

    async def set_current_database_config(self, config_id: int) -> Dict[str, Any]:
        """设置当前使用的数据库配置"""
        try:
            logger.info("设置当前数据库配置", config_id=config_id)
            
            from app.core.database import engine
            async with engine.begin() as conn:
                db = AsyncSession(bind=conn)
                
                # 首先取消所有配置的默认状态
                await db.execute(
                    update(DatabaseConfig).values(is_default=False)
                )
                
                # 设置指定配置为默认
                result = await db.execute(
                    update(DatabaseConfig)
                    .where(DatabaseConfig.id == config_id)
                    .values(is_default=True)
                )
                
                if result.rowcount == 0:
                    return {
                        "success": False,
                        "message": "配置不存在"
                    }
                
                logger.info("设置当前数据库配置成功", config_id=config_id)
                
                return {
                    "success": True,
                    "message": "当前配置设置成功"
                }
                
        except Exception as e:
            logger.error("设置当前数据库配置失败", error=str(e))
            return {
                "success": False,
                "message": f"设置当前配置失败: {str(e)}"
            }


# 全局配置数据库服务实例
config_db_service = ConfigDBService()
