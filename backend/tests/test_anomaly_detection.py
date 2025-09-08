#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常检测API测试用例
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app
from app.models.schemas import AlgorithmType

client = TestClient(app)

class TestAnomalyDetectionAPI:
    """异常检测API测试"""
    
    @pytest.fixture
    def mock_ai_detector(self):
        """模拟AI检测器"""
        with patch('app.api.v1.endpoints.anomaly_detection.ai_detector') as mock_detector:
            mock_detector.detect_anomalies = AsyncMock(return_value={
                "anomalies": [],
                "total_points": 100,
                "anomaly_count": 5,
                "overall_score": 0.85,
                "algorithm_used": AlgorithmType.ISOLATION_FOREST,
                "execution_time": 0.5,
                "recommendations": ["建议检查系统资源使用情况"],
                "model_info": {"algorithm": "isolation_forest"}
            })
            mock_detector.get_model_info = AsyncMock(return_value={
                "algorithms": ["isolation_forest", "z_score"],
                "default_algorithm": "isolation_forest"
            })
            yield mock_detector
    
    @pytest.fixture
    def mock_prometheus_service(self):
        """模拟Prometheus服务"""
        with patch('app.api.v1.endpoints.anomaly_detection.prometheus_service') as mock_service:
            mock_service.query_range = AsyncMock(return_value={
                "success": True,
                "message": "查询执行成功",
                "data": [],
                "query": "test_query",
                "execution_time": 0.1
            })
            yield mock_service
    
    def test_detect_anomalies(self, mock_ai_detector, mock_prometheus_service):
        """测试异常检测接口"""
        response = client.post("/api/v1/anomaly-detection/detect", json={
            "metric_query": "cpu_usage",
            "lookback_hours": 24,
            "algorithm": "isolation_forest",
            "sensitivity": 0.8
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        
    def test_get_algorithms(self, mock_ai_detector):
        """测试获取算法列表接口"""
        response = client.get("/api/v1/anomaly-detection/algorithms")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "algorithms" in data["data"]
        
    def test_get_model_info(self, mock_ai_detector):
        """测试获取模型信息接口"""
        response = client.get("/api/v1/anomaly-detection/models/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data

if __name__ == "__main__":
    pytest.main([__file__])