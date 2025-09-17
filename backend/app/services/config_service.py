#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理服务

提供系统配置的持久化存储和管理功能
支持Prometheus、AI、数据库等各类配置的CRUD操作
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class ConfigService:
    """配置管理服务"""
    
    def __init__(self):
        self.config_dir = Path(settings.CONFIG_DIR)
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "system_config.json"
        self._config_cache: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
                logger.info("配置加载成功", file=str(self.config_file))
            else:
                self._config_cache = self._get_default_config()
                self._save_config()
                logger.info("创建默认配置文件", file=str(self.config_file))
        except Exception as e:
            logger.error("配置加载失败", error=str(e))
            self._config_cache = self._get_default_config()
    
    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_cache, f, ensure_ascii=False, indent=2, default=self._json_serializer)
            logger.info("配置保存成功", file=str(self.config_file))
        except Exception as e:
            logger.error("配置保存失败", error=str(e))
            raise
    
    def _json_serializer(self, obj):
        """自定义JSON序列化器"""
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "prometheus": {
                "enabled": True,
                "url": str(settings.PROMETHEUS_URL),
                "timeout": settings.PROMETHEUS_TIMEOUT,
                "max_retries": settings.PROMETHEUS_MAX_RETRIES,
                "scrape_interval": "15s",
                "evaluation_interval": "15s",
                "targets": []
            },
            "ai": {
                "enabled": True,
                "model_path": str(getattr(settings, 'AI_MODEL_PATH', './models')),
                "batch_size": getattr(settings, 'AI_BATCH_SIZE', 1000),
                "max_workers": getattr(settings, 'AI_MAX_WORKERS', 4)
            },
            "database": {
                "url": settings.DATABASE_URL,
                "max_connections": getattr(settings, 'MAX_CONNECTIONS', 20),
                "connection_timeout": getattr(settings, 'CONNECTION_TIMEOUT', 30)
            },
            "system": {
                "app_name": settings.APP_NAME,
                "app_version": settings.APP_VERSION,
                "debug": settings.DEBUG,
                "environment": settings.ENVIRONMENT
            }
        }
    
    def get_config(self, section: str = None) -> Dict[str, Any]:
        """获取配置"""
        if section:
            return self._config_cache.get(section, {})
        return self._config_cache.copy()
    
    def update_config(self, section: str, config: Dict[str, Any]) -> None:
        """更新配置"""
        if section not in self._config_cache:
            self._config_cache[section] = {}
        
        self._config_cache[section].update(config)
        self._save_config()
        logger.info("配置更新成功", section=section, config=config)
    
    def get_prometheus_config(self) -> Dict[str, Any]:
        """获取Prometheus配置"""
        return self.get_config("prometheus")
    
    def update_prometheus_config(self, config: Dict[str, Any]) -> None:
        """更新Prometheus配置"""
        self.update_config("prometheus", config)
    
    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI配置"""
        return self.get_config("ai")
    
    def update_ai_config(self, config: Dict[str, Any]) -> None:
        """更新AI配置"""
        self.update_config("ai", config)
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.get_config("database")
    
    def update_database_config(self, config: Dict[str, Any]) -> None:
        """更新数据库配置"""
        self.update_config("database", config)


# 全局配置服务实例
config_service = ConfigService()
