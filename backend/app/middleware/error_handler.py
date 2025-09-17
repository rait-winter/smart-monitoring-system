#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一错误处理中间件

提供全局错误处理、日志记录、错误分类和响应格式化功能
支持不同环境的错误信息展示和错误监控集成

主要功能:
1. 全局异常捕获和处理
2. 错误分类和严重程度评估
3. 结构化错误日志记录
4. 错误响应标准化
5. 错误监控和告警集成
"""

import traceback
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional


class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理datetime等特殊类型"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
from enum import Enum

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog

from app.core.config import settings
from app.models.schemas import APIResponse

logger = structlog.get_logger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误分类"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    NETWORK = "network"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self):
        self.logger = logger.bind(component="ErrorHandler")
    
    def classify_error(self, error: Exception) -> ErrorCategory:
        """分类错误类型"""
        error_name = type(error).__name__.lower()
        error_message = str(error).lower()
        
        if isinstance(error, RequestValidationError):
            return ErrorCategory.VALIDATION
        elif isinstance(error, HTTPException):
            if error.status_code == 401:
                return ErrorCategory.AUTHENTICATION
            elif error.status_code == 403:
                return ErrorCategory.AUTHORIZATION
            elif error.status_code == 404:
                return ErrorCategory.NOT_FOUND
            else:
                return ErrorCategory.BUSINESS_LOGIC
        elif "database" in error_name or "sql" in error_message:
            return ErrorCategory.DATABASE
        elif "network" in error_name or "connection" in error_message:
            return ErrorCategory.NETWORK
        elif "external" in error_message or "api" in error_message:
            return ErrorCategory.EXTERNAL_SERVICE
        else:
            return ErrorCategory.INTERNAL
    
    def assess_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """评估错误严重程度"""
        if isinstance(error, HTTPException):
            if error.status_code >= 500:
                return ErrorSeverity.CRITICAL
            elif error.status_code >= 400:
                return ErrorSeverity.HIGH
            else:
                return ErrorSeverity.MEDIUM
        
        if category == ErrorCategory.DATABASE:
            return ErrorSeverity.CRITICAL
        elif category == ErrorCategory.EXTERNAL_SERVICE:
            return ErrorSeverity.HIGH
        elif category == ErrorCategory.VALIDATION:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def create_error_response(
        self,
        error: Exception,
        request: Request,
        error_id: str,
        category: ErrorCategory,
        severity: ErrorSeverity
    ) -> JSONResponse:
        """创建标准化错误响应"""
        
        # 基础错误信息
        error_info = {
            "error_id": error_id,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "method": request.method,
            "category": category.value,
            "severity": severity.value
        }
        
        # 根据环境决定是否显示详细错误信息
        if settings.is_production:
            # 生产环境：隐藏敏感信息
            if isinstance(error, HTTPException):
                message = error.detail
                status_code = error.status_code
            else:
                message = "服务器内部错误"
                status_code = 500
        else:
            # 开发环境：显示详细错误信息
            if isinstance(error, HTTPException):
                message = error.detail
                status_code = error.status_code
            else:
                message = str(error)
                status_code = 500
            
            # 添加调试信息
            error_info.update({
                "error_type": type(error).__name__,
                "traceback": traceback.format_exc().split('\n') if settings.DEBUG else None
            })
        
        # 创建API响应
        api_response = APIResponse(
            success=False,
            message=message,
            data=error_info
        )
        
        return JSONResponse(
            status_code=status_code,
            content=api_response.model_dump(mode='json'),
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    
    def log_error(
        self,
        error: Exception,
        request: Request,
        error_id: str,
        category: ErrorCategory,
        severity: ErrorSeverity
    ) -> None:
        """记录错误日志"""
        
        log_data = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "category": category.value,
            "severity": severity.value,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "traceback": traceback.format_exc() if settings.DEBUG else None
        }
        
        # 根据严重程度选择日志级别
        if severity == ErrorSeverity.CRITICAL:
            self.logger.error("严重错误", **log_data)
        elif severity == ErrorSeverity.HIGH:
            self.logger.error("高级错误", **log_data)
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning("中级错误", **log_data)
        else:
            self.logger.info("低级错误", **log_data)
    
    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """处理异常"""
        
        # 生成错误ID
        error_id = str(uuid.uuid4())
        
        # 分类和评估错误
        category = self.classify_error(exc)
        severity = self.assess_severity(exc, category)
        
        # 记录错误日志
        self.log_error(exc, request, error_id, category, severity)
        
        # 创建错误响应
        return self.create_error_response(exc, request, error_id, category, severity)


# 创建全局错误处理器实例
error_handler = ErrorHandler()


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    return await error_handler.handle_exception(request, exc)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    return await error_handler.handle_exception(request, exc)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """验证异常处理器"""
    return await error_handler.handle_exception(request, exc)


async def starlette_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Starlette异常处理器"""
    return await error_handler.handle_exception(request, exc)


# 错误统计和监控
class ErrorMonitor:
    """错误监控器"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_history: list = []
        self.max_history = 1000
    
    def record_error(self, category: ErrorCategory, severity: ErrorSeverity) -> None:
        """记录错误统计"""
        key = f"{category.value}:{severity.value}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # 添加到历史记录
        self.error_history.append({
            "timestamp": datetime.utcnow(),
            "category": category.value,
            "severity": severity.value
        })
        
        # 限制历史记录长度
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        return {
            "error_counts": self.error_counts.copy(),
            "total_errors": sum(self.error_counts.values()),
            "recent_errors": self.error_history[-100:] if self.error_history else [],
            "error_rate_by_category": {
                category.value: sum(
                    count for key, count in self.error_counts.items() 
                    if key.startswith(f"{category.value}:")
                ) for category in ErrorCategory
            }
        }


# 创建全局错误监控器
error_monitor = ErrorMonitor()
