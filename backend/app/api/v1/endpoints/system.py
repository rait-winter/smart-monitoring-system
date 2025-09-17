#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统管理API端点 - 健康检查和统计信息

提供系统健康状态监控、统计数据查询和
仪表盘数据聚合等管理功能。

端点功能:
1. GET /health - 系统健康检查
2. GET /statistics - 系统统计信息
3. GET /dashboard - 仪表盘数据

作者: AI监控团队
版本: 2.0.0
"""

import time
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Body
import structlog

from app.models.schemas import (
    HealthCheckResponse,
    SystemStats,
    DashboardData,
    APIResponse
)
from app.core.config import settings
from app.services.prometheus_service import PrometheusService
from app.middleware.performance import (
    get_performance_metrics,
    get_slow_requests,
    get_error_requests
)

logger = structlog.get_logger(__name__)

# 创建路由器
router = APIRouter()

# 系统启动时间
SYSTEM_START_TIME = time.time()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """系统健康检查"""
    try:
        uptime = time.time() - SYSTEM_START_TIME
        
        # 检查各组件状态
        components = {
            "database": "healthy",     # 实际应该检查数据库连接
            "prometheus": "healthy",   # 实际应该检查Prometheus连接
            "redis": "healthy",        # 实际应该检查Redis连接
            "ai_service": "healthy",   # 实际应该检查AI服务状态
            "notification": "healthy"  # 实际应该检查通知服务状态
        }
        
        return HealthCheckResponse(
            success=True,
            message="系统运行正常",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
            uptime=uptime,
            components=components
        )
        
    except Exception as e:
        logger.error("健康检查失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prometheus/test", response_model=APIResponse)
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


@router.get("/statistics", response_model=APIResponse)
async def get_system_statistics() -> APIResponse:
    """获取系统统计信息"""
    try:
        # 模拟统计数据（实际应该从各服务获取真实数据）
        stats = SystemStats(
            total_metrics=150,
            active_rules=25,
            alerts_last_24h=12,
            anomalies_detected=8,
            system_uptime=f"{(time.time() - SYSTEM_START_TIME) / 3600:.1f}小时",
            last_inspection=datetime.now(),
            prometheus_targets={
                "up": 45,
                "down": 2,
                "unknown": 1
            }
        )
        
        return APIResponse(
            success=True,
            message="获取系统统计成功",
            data={"statistics": stats}
        )
        
    except Exception as e:
        logger.error("获取系统统计失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_model=APIResponse)
async def get_dashboard_data() -> APIResponse:
    """获取仪表盘数据"""
    try:
        # 系统统计
        stats = SystemStats(
            total_metrics=150,
            active_rules=25,
            alerts_last_24h=12,
            anomalies_detected=8,
            system_uptime=f"{(time.time() - SYSTEM_START_TIME) / 3600:.1f}小时",
            last_inspection=datetime.now(),
            prometheus_targets={"up": 45, "down": 2, "unknown": 1}
        )
        
        # 最近告警（模拟数据）
        recent_alerts = [
            {
                "id": 1,
                "title": "CPU使用率过高",
                "severity": "high",
                "timestamp": "2025-09-06T20:30:00",
                "status": "resolved"
            },
            {
                "id": 2,
                "title": "内存使用率异常",
                "severity": "medium",
                "timestamp": "2025-09-06T19:45:00",
                "status": "active"
            }
        ]
        
        # 重要指标（模拟数据）
        top_metrics = [
            {"name": "cpu_usage_percent", "value": 75.2, "trend": "up"},
            {"name": "memory_usage_percent", "value": 68.5, "trend": "stable"},
            {"name": "disk_usage_percent", "value": 45.8, "trend": "down"},
            {"name": "network_io_bytes", "value": 1024000, "trend": "up"}
        ]
        
        # 系统健康状态
        system_health = {
            "overall_status": "healthy",
            "cpu_health": "good",
            "memory_health": "warning", 
            "disk_health": "good",
            "network_health": "good"
        }
        
        dashboard_data = DashboardData(
            stats=stats,
            recent_alerts=recent_alerts,
            top_metrics=top_metrics,
            system_health=system_health
        )
        
        return APIResponse(
            success=True,
            message="获取仪表盘数据成功",
            data={"dashboard": dashboard_data}
        )
        
    except Exception as e:
        logger.error("获取仪表盘数据失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/version", response_model=APIResponse)
async def get_version_info() -> APIResponse:
    """获取版本信息"""
    return APIResponse(
        success=True,
        message="获取版本信息成功",
        data={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": settings.APP_DESCRIPTION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        }
    )


@router.get("/performance", response_model=APIResponse)
async def get_performance_info() -> APIResponse:
    """获取性能监控信息"""
    try:
        metrics = await get_performance_metrics()
        return APIResponse(
            success=True,
            message="获取性能信息成功",
            data=metrics
        )
    except Exception as e:
        logger.error("获取性能信息失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/slow-requests", response_model=APIResponse)
async def get_slow_requests_info(limit: int = 10) -> APIResponse:
    """获取慢请求信息"""
    try:
        slow_requests = await get_slow_requests(limit)
        return APIResponse(
            success=True,
            message="获取慢请求信息成功",
            data={"slow_requests": slow_requests}
        )
    except Exception as e:
        logger.error("获取慢请求信息失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/error-requests", response_model=APIResponse)
async def get_error_requests_info(limit: int = 10) -> APIResponse:
    """获取错误请求信息"""
    try:
        error_requests = await get_error_requests(limit)
        return APIResponse(
            success=True,
            message="获取错误请求信息成功",
            data={"error_requests": error_requests}
        )
    except Exception as e:
        logger.error("获取错误请求信息失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))