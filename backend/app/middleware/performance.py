#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能监控中间件

提供请求性能监控、慢查询检测、资源使用统计等功能
支持性能指标收集、告警和优化建议

主要功能:
1. 请求响应时间监控
2. 慢查询检测和告警
3. 内存和CPU使用监控
4. 数据库查询性能统计
5. 性能指标导出和分析
"""

import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict, deque

try:
    import psutil
except ImportError:
    psutil = None

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    request_id: str
    path: str
    method: str
    start_time: float
    end_time: float
    duration_ms: float
    status_code: int
    memory_usage_mb: float
    cpu_percent: float
    db_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    slow_queries: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.logger = logger.bind(component="PerformanceMonitor")
        
        # 性能指标存储
        self.metrics_history: deque = deque(maxlen=10000)
        self.slow_requests: deque = deque(maxlen=1000)
        self.error_requests: deque = deque(maxlen=1000)
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "avg_response_time": 0.0,
            "max_response_time": 0.0,
            "min_response_time": float('inf'),
            "error_rate": 0.0,
            "slow_request_rate": 0.0
        }
        
        # 阈值配置
        self.slow_request_threshold = 1000  # 1秒
        self.memory_warning_threshold = 80  # 80%
        self.cpu_warning_threshold = 80     # 80%
        
        # 系统资源监控
        self.system_stats = {
            "memory_percent": 0.0,
            "cpu_percent": 0.0,
            "disk_usage_percent": 0.0
        }
    
    def start_request(self, request: Request) -> PerformanceMetrics:
        """开始监控请求"""
        current_time = time.time()
        
        metrics = PerformanceMetrics(
            request_id=f"req_{int(current_time * 1000)}",
            path=request.url.path,
            method=request.method,
            start_time=current_time,
            end_time=0.0,
            duration_ms=0.0,
            status_code=0,
            memory_usage_mb=0.0,
            cpu_percent=0.0
        )
        
        return metrics
    
    def end_request(self, metrics: PerformanceMetrics, response: Response) -> None:
        """结束监控请求"""
        current_time = time.time()
        
        # 更新指标
        metrics.end_time = current_time
        metrics.duration_ms = (current_time - metrics.start_time) * 1000
        metrics.status_code = response.status_code
        
        # 获取系统资源使用情况
        if psutil:
            process = psutil.Process()
            metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            metrics.cpu_percent = process.cpu_percent()
        else:
            metrics.memory_usage_mb = 0.0
            metrics.cpu_percent = 0.0
        
        # 更新系统统计
        self._update_system_stats()
        
        # 记录指标
        self._record_metrics(metrics)
        
        # 检查慢请求
        if metrics.duration_ms > self.slow_request_threshold:
            self._handle_slow_request(metrics)
        
        # 检查错误请求
        if metrics.status_code >= 400:
            self._handle_error_request(metrics)
        
        # 更新统计信息
        self._update_stats(metrics)
        
        # 记录性能日志
        self._log_performance(metrics)
    
    def _update_system_stats(self) -> None:
        """更新系统资源统计"""
        if not psutil:
            return
            
        try:
            self.system_stats["memory_percent"] = psutil.virtual_memory().percent
            self.system_stats["cpu_percent"] = psutil.cpu_percent(interval=0.1)
            self.system_stats["disk_usage_percent"] = psutil.disk_usage('/').percent
        except Exception as e:
            self.logger.warning("获取系统资源信息失败", error=str(e))
    
    def _record_metrics(self, metrics: PerformanceMetrics) -> None:
        """记录性能指标"""
        self.metrics_history.append(metrics)
    
    def _handle_slow_request(self, metrics: PerformanceMetrics) -> None:
        """处理慢请求"""
        self.slow_requests.append(metrics)
        
        self.logger.warning(
            "检测到慢请求",
            request_id=metrics.request_id,
            path=metrics.path,
            method=metrics.method,
            duration_ms=round(metrics.duration_ms, 2),
            threshold_ms=self.slow_request_threshold
        )
    
    def _handle_error_request(self, metrics: PerformanceMetrics) -> None:
        """处理错误请求"""
        self.error_requests.append(metrics)
        
        self.logger.error(
            "请求处理失败",
            request_id=metrics.request_id,
            path=metrics.path,
            method=metrics.method,
            status_code=metrics.status_code,
            duration_ms=round(metrics.duration_ms, 2)
        )
    
    def _update_stats(self, metrics: PerformanceMetrics) -> None:
        """更新统计信息"""
        self.stats["total_requests"] += 1
        
        # 更新响应时间统计
        if metrics.duration_ms > self.stats["max_response_time"]:
            self.stats["max_response_time"] = metrics.duration_ms
        
        if metrics.duration_ms < self.stats["min_response_time"]:
            self.stats["min_response_time"] = metrics.duration_ms
        
        # 计算平均响应时间
        total_duration = sum(m.duration_ms for m in self.metrics_history)
        self.stats["avg_response_time"] = total_duration / len(self.metrics_history)
        
        # 计算错误率
        error_count = len(self.error_requests)
        self.stats["error_rate"] = error_count / self.stats["total_requests"] if self.stats["total_requests"] > 0 else 0
        
        # 计算慢请求率
        slow_count = len(self.slow_requests)
        self.stats["slow_request_rate"] = slow_count / self.stats["total_requests"] if self.stats["total_requests"] > 0 else 0
    
    def _log_performance(self, metrics: PerformanceMetrics) -> None:
        """记录性能日志"""
        if settings.DEBUG or metrics.duration_ms > 500:  # 只记录慢请求或调试模式
            self.logger.info(
                "请求性能指标",
                request_id=metrics.request_id,
                path=metrics.path,
                method=metrics.method,
                duration_ms=round(metrics.duration_ms, 2),
                status_code=metrics.status_code,
                memory_mb=round(metrics.memory_usage_mb, 2),
                cpu_percent=round(metrics.cpu_percent, 2)
            )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        recent_metrics = list(self.metrics_history)[-100:]  # 最近100个请求
        
        if not recent_metrics:
            return {
                "message": "暂无性能数据",
                "stats": self.stats,
                "system": self.system_stats
            }
        
        # 计算最近性能指标
        recent_durations = [m.duration_ms for m in recent_metrics]
        recent_errors = [m for m in recent_metrics if m.status_code >= 400]
        recent_slow = [m for m in recent_metrics if m.duration_ms > self.slow_request_threshold]
        
        return {
            "stats": self.stats,
            "system": self.system_stats,
            "recent_performance": {
                "avg_response_time": sum(recent_durations) / len(recent_durations),
                "max_response_time": max(recent_durations),
                "min_response_time": min(recent_durations),
                "error_count": len(recent_errors),
                "slow_request_count": len(recent_slow),
                "sample_size": len(recent_metrics)
            },
            "warnings": self._check_warnings()
        }
    
    def _check_warnings(self) -> List[str]:
        """检查性能警告"""
        warnings = []
        
        if self.system_stats["memory_percent"] > self.memory_warning_threshold:
            warnings.append(f"内存使用率过高: {self.system_stats['memory_percent']:.1f}%")
        
        if self.system_stats["cpu_percent"] > self.cpu_warning_threshold:
            warnings.append(f"CPU使用率过高: {self.system_stats['cpu_percent']:.1f}%")
        
        if self.stats["error_rate"] > 0.05:  # 错误率超过5%
            warnings.append(f"错误率过高: {self.stats['error_rate']:.2%}")
        
        if self.stats["slow_request_rate"] > 0.1:  # 慢请求率超过10%
            warnings.append(f"慢请求率过高: {self.stats['slow_request_rate']:.2%}")
        
        return warnings
    
    def get_slow_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取慢请求列表"""
        slow_requests = list(self.slow_requests)[-limit:]
        
        return [
            {
                "request_id": req.request_id,
                "path": req.path,
                "method": req.method,
                "duration_ms": round(req.duration_ms, 2),
                "status_code": req.status_code,
                "timestamp": datetime.fromtimestamp(req.start_time).isoformat()
            }
            for req in slow_requests
        ]
    
    def get_error_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取错误请求列表"""
        error_requests = list(self.error_requests)[-limit:]
        
        return [
            {
                "request_id": req.request_id,
                "path": req.path,
                "method": req.method,
                "status_code": req.status_code,
                "duration_ms": round(req.duration_ms, 2),
                "timestamp": datetime.fromtimestamp(req.start_time).isoformat()
            }
            for req in error_requests
        ]


# 创建全局性能监控器
performance_monitor = PerformanceMonitor()


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.monitor = performance_monitor
    
    async def dispatch(self, request: Request, call_next):
        # 开始监控
        metrics = self.monitor.start_request(request)
        
        try:
            # 执行请求
            response = await call_next(request)
            
            # 结束监控
            self.monitor.end_request(metrics, response)
            
            return response
            
        except Exception as e:
            # 处理异常情况
            metrics.status_code = 500
            metrics.errors.append(str(e))
            self.monitor.end_request(metrics, Response(status_code=500))
            raise


# 性能监控API端点
async def get_performance_metrics() -> Dict[str, Any]:
    """获取性能指标API"""
    return performance_monitor.get_performance_summary()


async def get_slow_requests(limit: int = 10) -> List[Dict[str, Any]]:
    """获取慢请求API"""
    return performance_monitor.get_slow_requests(limit)


async def get_error_requests(limit: int = 10) -> List[Dict[str, Any]]:
    """获取错误请求API"""
    return performance_monitor.get_error_requests(limit)
