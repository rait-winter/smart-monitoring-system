#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CORS配置解析
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import Settings

def test_cors_parsing():
    """测试CORS配置解析"""
    print("🔍 测试CORS配置解析...")
    
    # 创建设置实例
    settings = Settings()
    
    print(f"✅ CORS origins类型: {type(settings.BACKEND_CORS_ORIGINS)}")
    print(f"✅ CORS origins值: {settings.BACKEND_CORS_ORIGINS}")
    
    # 检查是否包含特定的前端地址
    expected_origin = "http://192.168.10.35:3000"
    cors_origins_str = [str(url) for url in settings.BACKEND_CORS_ORIGINS]
    
    print(f"📋 CORS origins字符串列表: {cors_origins_str}")
    
    if expected_origin in cors_origins_str:
        print(f"✅ 配置正确包含前端地址: {expected_origin}")
        return True
    else:
        print(f"❌ 配置缺失前端地址: {expected_origin}")
        return False

if __name__ == "__main__":
    test_cors_parsing()