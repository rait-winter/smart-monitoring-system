#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统管理API测试用例
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app
from app.models.schemas import HealthCheckResponse

client = TestClient(app)

class TestSystemAPI:
    """系统管理API测试"""
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "service" in data["data"]
        assert "version" in data["data"]
        
    def test_root_endpoint(self):
        """测试根路径接口"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert "version" in data
        
    def test_version_info(self):
        """测试版本信息接口"""
        response = client.get("/api/v1/system/version")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data

if __name__ == "__main__":
    pytest.main([__file__])