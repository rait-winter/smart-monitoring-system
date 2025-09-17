#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prometheus配置管理API端点

提供Prometheus数据源配置管理功能，包括：
1. 获取Prometheus配置
2. 更新Prometheus配置
3. 测试Prometheus连接

作者: AI监控团队
版本: 2.0.0
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import Response
import structlog

from app.models.schemas import APIResponse
from app.core.config import settings
from app.services.prometheus_service import PrometheusService
from app.services.config_service import config_service
from app.services.config_db_service import config_db_service

logger = structlog.get_logger(__name__)

# 创建路由器
router = APIRouter()


@router.get("/config", response_model=APIResponse)
async def get_prometheus_config() -> APIResponse:
    """获取Prometheus配置"""
    try:
        # 优先从数据库获取配置
        db_config = await config_db_service.get_default_prometheus_config()
        if db_config:
            config = {
                "enabled": db_config["is_enabled"],
                "url": db_config["url"],
                "username": db_config["username"],
                "password": db_config["password"],
                "timeout": db_config["timeout"],
                "scrapeInterval": db_config["scrape_interval"],
                "evaluationInterval": db_config["evaluation_interval"],
                "max_retries": db_config["max_retries"],
                "targets": []
            }
        else:
            # 从配置文件获取默认配置
            config = config_service.get_prometheus_config()
        
        return APIResponse(
            success=True,
            message="获取Prometheus配置成功",
            data={"config": config}
        )
        
    except Exception as e:
        logger.error("获取Prometheus配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config", response_model=APIResponse)
async def update_prometheus_config(config: Dict[str, Any] = Body(..., description="Prometheus配置")) -> APIResponse:
    """更新Prometheus配置"""
    try:
        # 保存配置到数据库
        result = await config_db_service.save_prometheus_config(config)
        
        # 同时保存到配置文件作为备份
        config_service.update_prometheus_config(config)
        
        return APIResponse(
            success=True,
            message="Prometheus配置更新成功",
            data=result
        )
        
    except Exception as e:
        logger.error("更新Prometheus配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.options("/test")
async def test_prometheus_connection_options(request: Request) -> Response:
    """处理OPTIONS预检请求"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400"
        }
    )


@router.post("/test", response_model=APIResponse)
async def test_prometheus_connection(config: Dict[str, Any] = Body(..., description="Prometheus配置")) -> APIResponse:
    """测试Prometheus连接"""
    try:
        # 创建临时Prometheus服务实例用于测试
        prometheus_service = PrometheusService()
        
        # 如果提供了URL，则使用提供的URL
        if "url" in config and config["url"]:
            prometheus_service.base_url = config["url"].rstrip('/')
        
        # 执行健康检查
        is_healthy = await prometheus_service.health_check()
        
        if is_healthy:
            return APIResponse(
                success=True,
                message="Prometheus连接测试成功",
                data={"healthy": True}
            )
        else:
            return APIResponse(
                success=False,
                message="Prometheus连接测试失败，请检查配置",
                data={"healthy": False}
            )
            
    except Exception as e:
        logger.error("Prometheus连接测试失败", error=str(e))
        return APIResponse(
            success=False,
            message=f"Prometheus连接测试失败: {str(e)}",
            data={"healthy": False, "error": str(e)}
        )