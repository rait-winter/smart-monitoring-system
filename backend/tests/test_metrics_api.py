#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标查询API测试用例
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import asyncio

from main import app

client = TestClient(app)

class TestMetricsAPI:
    """指标查询API测试"""
    
    @pytest.fixture
    def mock_prometheus_service(self):
        """模拟Prometheus服务"""
        with patch('app.api.v1.endpoints.metrics.prometheus_service') as mock_service:
            mock_service.query_range = AsyncMock(return_value={
                "success": True,
                "message": "查询执行成功",
                "data": [],
                "query": "test_query",
                "execution_time": 0.1
            })
            mock_service.query_instant = AsyncMock(return_value={
                "status": "success",
                "data": {"result": []}
            })
            mock_service.health_check = AsyncMock(return_value=True)
            yield mock_service
    
    def test_query_range(self, mock_prometheus_service):
        """测试范围查询接口"""
        response = client.post("/api/v1/metrics/query_range", json={
            "query": "cpu_usage",
            "start_time": "2023-01-01T00:00:00",
            "end_time": "2023-01-01T01:00:00",
            "step": "1m"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
    def test_query_instant(self, mock_prometheus_service):
        """测试即时查询接口"""
        response = client.post("/api/v1/metrics/query", json={
            "query": "cpu_usage"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
    def test_prometheus_health(self, mock_prometheus_service):
        """测试Prometheus健康检查"""
        response = client.get("/api/v1/metrics/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["healthy"] is True

if __name__ == "__main__":
    pytest.main([__file__])