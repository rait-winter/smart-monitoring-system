#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API v1 主路由 - 智能监控预警系统

集成所有API端点，提供完整的监控、分析、告警功能。
包含异常检测、规则管理、通知服务等核心API。

功能模块:
1. 异常检测API - AI驱动的异常识别
2. 规则管理API - 巡检规则CRUD
3. 通知服务API - 多渠道告警通知  
4. 指标查询API - Prometheus数据接口
5. 系统管理API - 健康检查和统计

作者: AI监控团队
版本: 2.0.0
"""

from fastapi import APIRouter
from .endpoints import (
    anomaly_detection,
    rules,
    notifications,
    metrics,
    system,
    prometheus,
    ollama
)

# 创建API v1路由器
api_router = APIRouter()

# 注册各功能模块路由
api_router.include_router(
    anomaly_detection.router,
    prefix="/anomaly-detection",
    tags=["AI异常检测"]
)

api_router.include_router(
    rules.router,
    prefix="/rules",
    tags=["规则引擎"]
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["通知服务"]
)

api_router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["指标查询"]
)

api_router.include_router(
    system.router,
    prefix="/system",
    tags=["系统管理"]
)

# 注册Prometheus配置管理路由
api_router.include_router(
    prometheus.router,
    prefix="/prometheus",
    tags=["Prometheus配置"]
)

# 注册Ollama配置管理路由
api_router.include_router(
    ollama.router,
    prefix="/ollama",
    tags=["Ollama配置"]
)

# 根路径信息
@api_router.get("/", tags=["API信息"])
async def api_info():
    """API v1信息"""
    return {
        "name": "智能监控预警系统 API",
        "version": "v1",
        "description": "基于AI的自动化巡检与智能预警API接口",
        "modules": [
            "anomaly-detection - AI异常检测",
            "rules - 规则引擎管理",
            "notifications - 通知服务",
            "metrics - 指标数据查询",
            "system - 系统管理",
            "prometheus - Prometheus配置管理",
            "ollama - Ollama AI配置管理"
        ],
        "docs": "/docs",
        "openapi": "/openapi.json"
    }