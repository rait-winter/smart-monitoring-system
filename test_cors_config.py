#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端CORS配置
"""

import os
from dotenv import load_dotenv

# 加载环境变量
print("加载环境变量...")
env_files = [".env", ".env.development", "../.env", "../.env.development"]
loaded_env = None
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"加载环境文件: {env_file}")
        load_dotenv(env_file)
        loaded_env = env_file
        break

print(f"已加载环境文件: {loaded_env}")

# 检查环境变量
cors_origins = os.getenv('BACKEND_CORS_ORIGINS')
print(f"BACKEND_CORS_ORIGINS: {cors_origins}")

# 检查Pydantic配置
print("\n检查Pydantic配置...")
try:
    from app.core.config import settings
    print(f"配置实例 BACKEND_CORS_ORIGINS: {settings.BACKEND_CORS_ORIGINS}")
    print(f"配置实例类型: {type(settings.BACKEND_CORS_ORIGINS)}")
    
    # 检查是否包含我们需要的地址
    expected_origin = "http://192.168.10.35:3000"
    if expected_origin in [str(url) for url in settings.BACKEND_CORS_ORIGINS]:
        print(f"✓ 配置中包含 {expected_origin}")
    else:
        print(f"✗ 配置中不包含 {expected_origin}")
        
except Exception as e:
    print(f"配置加载失败: {e}")
    import traceback
    traceback.print_exc()