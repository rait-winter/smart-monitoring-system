#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查后端配置
"""

import os
import sys

# 添加后端目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 加载环境变量
from dotenv import load_dotenv
env_files = ["backend/.env", "backend/.env.development", ".env", ".env.development"]
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"加载环境文件: {env_file}")
        load_dotenv(env_file)
        break

# 检查环境变量
print("环境变量检查:")
print(f"  BACKEND_CORS_ORIGINS: {os.getenv('BACKEND_CORS_ORIGINS')}")

# 检查Pydantic配置
try:
    # 更改工作目录到后端目录
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_path)
    
    from app.core.config import settings
    print("\nPydantic配置检查:")
    print(f"  BACKEND_CORS_ORIGINS: {settings.BACKEND_CORS_ORIGINS}")
    
    # 检查是否包含我们需要的地址
    expected_origin = "http://192.168.10.35:3000"
    cors_origins_str = [str(url).rstrip('/') for url in settings.BACKEND_CORS_ORIGINS]
    print(f"  CORS源列表(去除末尾斜杠): {cors_origins_str}")
    
    if expected_origin in cors_origins_str:
        print(f"  ✓ 配置中包含 {expected_origin}")
    else:
        print(f"  ✗ 配置中不包含 {expected_origin}")
        
    # 也检查带斜杠的版本
    expected_origin_with_slash = "http://192.168.10.35:3000/"
    if expected_origin_with_slash in [str(url) for url in settings.BACKEND_CORS_ORIGINS]:
        print(f"  ✓ 配置中包含 {expected_origin_with_slash}")
    else:
        print(f"  ✗ 配置中不包含 {expected_origin_with_slash}")
        
except Exception as e:
    print(f"配置加载失败: {e}")
    import traceback
    traceback.print_exc()