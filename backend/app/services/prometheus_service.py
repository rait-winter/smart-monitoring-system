#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prometheus数据服务 - 时间序列数据采集与查询

负责与Prometheus服务器通信，执行PromQL查询，
获取监控指标数据，为异常检测提供数据源。

功能特性:
1. Prometheus连接和健康检查
2. PromQL查询执行
3. 时间序列数据解析
4. 查询结果缓存优化
5. 错误处理和重试机制
6. 指标元数据管理

作者: AI监控团队
版本: 2.0.0
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin
import json

import httpx
import structlog
from cachetools import TTLCache

from app.core.config import settings
from app.models.schemas import (
    MetricsQueryRequest,
    MetricsResponse, 
    TimeSeriesData,
    MetricDataPoint,
    APIResponse
)

logger = structlog.get_logger(__name__)


class PrometheusService:
    """
    Prometheus数据服务
    
    提供与Prometheus服务器的完整交互功能，
    包括查询执行、数据解析、缓存管理等。
    
    核心功能:
    1. 执行PromQL查询获取时间序列数据
    2. 解析Prometheus响应格式
    3. 提供查询结果缓存
    4. 健康检查和连接管理
    5. 错误处理和自动重试
    
    使用示例:
        service = PrometheusService()
        
        # 查询指标数据
        result = await service.query_range(
            query="cpu_usage_percent", 
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now()
        )
        
        # 检查连接状态
        is_healthy = await service.health_check()
    """
    
    def __init__(self):
        """初始化Prometheus服务"""
        self.logger = logger.bind(component="PrometheusService")
        
        # 服务器配置
        self.base_url = str(settings.PROMETHEUS_URL).rstrip('/')
        self.timeout = settings.PROMETHEUS_TIMEOUT
        self.max_retries = settings.PROMETHEUS_MAX_RETRIES
        
        # HTTP客户端配置
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=5)
        )
        
        # 查询结果缓存 - TTL=30秒
        self.query_cache = TTLCache(maxsize=100, ttl=30)
        
        self.logger.info(
            "Prometheus服务初始化完成",
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
    
    
    async def query_range(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        step: str = "1m"
    ) -> MetricsResponse:
        """
        执行范围查询获取时间序列数据
        
        Args:
            query: PromQL查询语句
            start_time: 查询开始时间
            end_time: 查询结束时间  
            step: 查询步长，如"1m", "5m", "1h"
            
        Returns:
            MetricsResponse: 查询结果包含时间序列数据
            
        Raises:
            httpx.HTTPError: HTTP请求失败
            ValueError: 查询参数无效
            RuntimeError: Prometheus服务器错误
        """
        execution_start = time.time()
        
        try:
            # 参数验证
            if not query.strip():
                raise ValueError("查询语句不能为空")
            
            if start_time >= end_time:
                raise ValueError("开始时间必须早于结束时间")
            
            # 检查缓存
            cache_key = f"{query}:{start_time.isoformat()}:{end_time.isoformat()}:{step}"
            if cache_key in self.query_cache:
                self.logger.debug("使用缓存查询结果", query=query)
                return self.query_cache[cache_key]
            
            self.logger.info(
                "执行Prometheus范围查询",
                query=query,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                step=step
            )
            
            # 构建查询参数
            params = {
                "query": query,
                "start": start_time.timestamp(),
                "end": end_time.timestamp(),
                "step": step
            }
            
            # 执行查询
            url = urljoin(self.base_url, "/api/v1/query_range")
            response_data = await self._execute_request("GET", url, params=params)
            
            # 解析响应数据
            time_series_data = await self._parse_range_response(response_data)
            
            execution_time = time.time() - execution_start
            
            # 构建响应
            metrics_response = MetricsResponse(
                success=True,
                message="查询执行成功",
                data=time_series_data,
                query=query,
                execution_time=execution_time
            )
            
            # 缓存结果
            self.query_cache[cache_key] = metrics_response
            
            self.logger.info(
                "Prometheus查询完成",
                query=query,
                series_count=len(time_series_data),
                total_points=sum(len(ts.values) for ts in time_series_data),
                execution_time=round(execution_time, 3)
            )
            
            return metrics_response
            
        except Exception as e:
            execution_time = time.time() - execution_start
            self.logger.error(
                "Prometheus查询失败",
                query=query,
                error=str(e),
                execution_time=round(execution_time, 3)
            )
            raise RuntimeError(f"Prometheus查询失败: {str(e)}")
    
    
    async def query_instant(self, query: str, timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """
        执行即时查询获取单个时间点数据
        
        Args:
            query: PromQL查询语句
            timestamp: 查询时间点，None表示当前时间
            
        Returns:
            Dict: 查询结果数据
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            self.logger.info("执行Prometheus即时查询", query=query, timestamp=timestamp.isoformat())
            
            params = {
                "query": query,
                "time": timestamp.timestamp()
            }
            
            url = urljoin(self.base_url, "/api/v1/query")
            response_data = await self._execute_request("GET", url, params=params)
            
            return response_data
            
        except Exception as e:
            self.logger.error("Prometheus即时查询失败", query=query, error=str(e))
            raise RuntimeError(f"Prometheus即时查询失败: {str(e)}")
    
    
    async def health_check(self) -> bool:
        """
        检查Prometheus服务器健康状态
        
        Returns:
            bool: True表示健康，False表示不可用
        """
        try:
            url = urljoin(self.base_url, "/-/healthy")
            response = await self.client.get(url, timeout=5.0)
            
            is_healthy = response.status_code == 200
            
            self.logger.info(
                "Prometheus健康检查",
                status_code=response.status_code,
                is_healthy=is_healthy
            )
            
            return is_healthy
            
        except Exception as e:
            self.logger.warning("Prometheus健康检查失败", error=str(e))
            return False
    
    
    async def get_label_values(self, label_name: str) -> List[str]:
        """
        获取指定标签的所有可能值
        
        Args:
            label_name: 标签名称
            
        Returns:
            List[str]: 标签值列表
        """
        try:
            url = urljoin(self.base_url, f"/api/v1/label/{label_name}/values")
            response_data = await self._execute_request("GET", url)
            
            if response_data.get("status") == "success":
                return response_data.get("data", [])
            else:
                raise RuntimeError(f"获取标签值失败: {response_data.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error("获取标签值失败", label_name=label_name, error=str(e))
            raise RuntimeError(f"获取标签值失败: {str(e)}")
    
    
    async def get_metrics_metadata(self) -> Dict[str, Any]:
        """
        获取指标元数据信息
        
        Returns:
            Dict: 指标元数据，包含指标名称、类型、帮助信息等
        """
        try:
            url = urljoin(self.base_url, "/api/v1/metadata")
            response_data = await self._execute_request("GET", url)
            
            if response_data.get("status") == "success":
                return response_data.get("data", {})
            else:
                raise RuntimeError(f"获取指标元数据失败: {response_data.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error("获取指标元数据失败", error=str(e))
            raise RuntimeError(f"获取指标元数据失败: {str(e)}")
    
    
    async def _execute_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        执行HTTP请求，包含重试机制
        
        Args:
            method: HTTP方法
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            Dict: 响应数据
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.debug(
                    "执行HTTP请求",
                    method=method,
                    url=url,
                    attempt=attempt + 1,
                    max_retries=self.max_retries + 1
                )
                
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                
                return response.json()
                
            except httpx.HTTPError as e:
                last_error = e
                self.logger.warning(
                    "HTTP请求失败，准备重试",
                    method=method,
                    url=url,
                    attempt=attempt + 1,
                    error=str(e)
                )
                
                if attempt < self.max_retries:
                    # 指数退避重试
                    await asyncio.sleep(2 ** attempt)
                
            except Exception as e:
                self.logger.error("HTTP请求发生非预期错误", method=method, url=url, error=str(e))
                raise
        
        # 所有重试都失败
        raise RuntimeError(f"HTTP请求失败，已重试{self.max_retries}次: {str(last_error)}")
    
    
    async def _parse_range_response(self, response_data: Dict[str, Any]) -> List[TimeSeriesData]:
        """
        解析Prometheus范围查询响应
        
        Args:
            response_data: Prometheus API响应数据
            
        Returns:
            List[TimeSeriesData]: 解析后的时间序列数据
        """
        try:
            if response_data.get("status") != "success":
                error_msg = response_data.get("error", "Unknown error")
                raise RuntimeError(f"Prometheus查询失败: {error_msg}")
            
            result = response_data.get("data", {}).get("result", [])
            time_series_list = []
            
            for series in result:
                # 解析指标信息
                metric_info = series.get("metric", {})
                metric_name = metric_info.pop("__name__", "unknown_metric")
                labels = metric_info
                
                # 解析数据点
                values_data = series.get("values", [])
                data_points = []
                
                for timestamp, value in values_data:
                    try:
                        data_point = MetricDataPoint(
                            timestamp=datetime.fromtimestamp(float(timestamp)),
                            value=float(value),
                            labels=labels.copy()
                        )
                        data_points.append(data_point)
                    except (ValueError, TypeError) as e:
                        self.logger.warning(
                            "跳过无效数据点",
                            timestamp=timestamp,
                            value=value,
                            error=str(e)
                        )
                        continue
                
                # 创建时间序列对象
                if data_points:  # 只添加有效数据点的序列
                    time_series = TimeSeriesData(
                        metric_name=metric_name,
                        labels=labels,
                        values=data_points
                    )
                    time_series_list.append(time_series)
            
            self.logger.debug(
                "Prometheus响应解析完成",
                series_count=len(time_series_list),
                total_points=sum(len(ts.values) for ts in time_series_list)
            )
            
            return time_series_list
            
        except Exception as e:
            self.logger.error("Prometheus响应解析失败", error=str(e))
            raise ValueError(f"响应解析失败: {str(e)}")
    
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出，关闭HTTP客户端"""
        await self.client.aclose()


# 导出类
__all__ = ["PrometheusService"]