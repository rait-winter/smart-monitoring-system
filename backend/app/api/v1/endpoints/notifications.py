#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知服务API端点 - 多渠道告警通知接口

提供通知发送、状态查询、渠道测试等功能。
支持Slack、邮件、Webhook等多种通知方式。

端点功能:
1. POST /send - 发送通知
2. GET /statistics - 通知统计
3. POST /test - 测试通知渠道

作者: AI监控团队
版本: 2.0.0
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
import structlog

from app.models.schemas import (
    NotificationRequest,
    NotificationResponse,
    APIResponse
)
from app.services.notification_service import NotificationService

logger = structlog.get_logger(__name__)

# 创建路由器
router = APIRouter()

# 服务实例
notification_service = NotificationService()


@router.post("/send", response_model=NotificationResponse)
async def send_notification(request: NotificationRequest) -> NotificationResponse:
    """发送通知"""
    try:
        response = await notification_service.send_notification_request(request)
        return response
    except Exception as e:
        logger.error("发送通知失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=APIResponse)
async def get_statistics() -> APIResponse:
    """获取通知统计信息"""
    try:
        stats = await notification_service.get_statistics()
        
        return APIResponse(
            success=True,
            message="获取通知统计成功",
            data=stats
        )
    except Exception as e:
        logger.error("获取通知统计失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test", response_model=APIResponse)
async def test_channels() -> APIResponse:
    """测试通知渠道可用性"""
    try:
        test_results = await notification_service.test_channels()
        
        return APIResponse(
            success=True,
            message="通知渠道测试完成",
            data={"channel_tests": test_results}
        )
    except Exception as e:
        logger.error("测试通知渠道失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))