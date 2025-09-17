#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端CORS配置加载
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

# 加载环境变量
from dotenv import load_dotenv
env_files = [".env", ".env.development", "../.env", "../.env.development"]
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"加载环境文件: {env_file}")
        load_dotenv(env_file)
        break

# 测试配置加载
try:
    from app.core.config import settings
    print("配置加载成功!")
    print(f"BACKEND_CORS_ORIGINS: {settings.BACKEND_CORS_ORIGINS}")
    
    # 检查是否包含我们需要的地址
    expected_origin = "http://192.168.10.35:3000"
    cors_origins_str = [str(url) for url in settings.BACKEND_CORS_ORIGINS]
    print(f"CORS源列表: {cors_origins_str}")
    
    if expected_origin in cors_origins_str:
        print(f"✓ 配置中包含 {expected_origin}")
    else:
        print(f"✗ 配置中不包含 {expected_origin}")
        
except Exception as e:
    print(f"配置加载失败: {e}")
    import traceback
    traceback.print_exc()