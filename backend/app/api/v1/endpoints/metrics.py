#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标查询API端点 - Prometheus数据接口

提供Prometheus指标数据查询功能，支持范围查询、
即时查询和元数据获取。

端点功能:
1. POST /query - 即时查询
2. POST /query_range - 范围查询
3. GET /labels - 获取标签列表
4. GET /metadata - 获取指标元数据

作者: AI监控团队
版本: 2.0.0
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Body, Query
import structlog

from app.models.schemas import (
    MetricsQueryRequest,
    MetricsResponse,
    APIResponse
)
from app.services.prometheus_service import PrometheusService

logger = structlog.get_logger(__name__)

# 创建路由器
router = APIRouter()

# 服务实例
prometheus_service = PrometheusService()


@router.post("/query_range", response_model=MetricsResponse)
async def query_range(request: MetricsQueryRequest) -> MetricsResponse:
    """执行Prometheus范围查询"""
    try:
        response = await prometheus_service.query_range(
            query=request.query,
            start_time=request.start_time,
            end_time=request.end_time,
            step=request.step
        )
        
        return response
    except Exception as e:
        logger.error("范围查询失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=APIResponse)
async def query_instant(
    query: str = Body(..., description="PromQL查询语句"),
    timestamp: Optional[datetime] = Body(None, description="查询时间点")
) -> APIResponse:
    """执行Prometheus即时查询"""
    try:
        result = await prometheus_service.query_instant(query, timestamp)
        
        return APIResponse(
            success=True,
            message="即时查询执行成功",
            data=result
        )
    except Exception as e:
        logger.error("即时查询失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=APIResponse)
async def check_prometheus_health() -> APIResponse:
    """检查Prometheus服务健康状态"""
    try:
        is_healthy = await prometheus_service.health_check()
        
        return APIResponse(
            success=is_healthy,
            message="Prometheus健康检查完成",
            data={"healthy": is_healthy}
        )
    except Exception as e:
        logger.error("健康检查失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/labels/{label_name}", response_model=APIResponse)
async def get_label_values(label_name: str) -> APIResponse:
    """获取指定标签的所有可能值"""
    try:
        values = await prometheus_service.get_label_values(label_name)
        
        return APIResponse(
            success=True,
            message=f"获取标签{label_name}的值成功",
            data={"label_name": label_name, "values": values}
        )
    except Exception as e:
        logger.error("获取标签值失败", label_name=label_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata", response_model=APIResponse)
async def get_metadata() -> APIResponse:
    """获取指标元数据"""
    try:
        metadata = await prometheus_service.get_metrics_metadata()
        
        return APIResponse(
            success=True,
            message="获取指标元数据成功",
            data=metadata
        )
    except Exception as e:
        logger.error("获取指标元数据失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))