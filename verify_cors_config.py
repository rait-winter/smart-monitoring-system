#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证后端实际使用的CORS配置
"""

import sys
import os

# 添加后端目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

print("当前工作目录:", os.getcwd())
print("后端路径:", backend_path)
print("Python路径:", sys.path[:3])

# 加载环境变量
from dotenv import load_dotenv

# 尝试加载后端目录中的.env文件
env_files = [
    os.path.join(backend_path, ".env"),
    os.path.join(backend_path, ".env.development"),
    ".env", 
    ".env.development"
]

for env_file in env_files:
    if os.path.exists(env_file):
        print(f"\n加载环境文件: {env_file}")
        load_dotenv(env_file, override=True)
        break
else:
    print("\n未找到环境文件")

# 检查环境变量
print("\n环境变量检查:")
cors_origins = os.getenv('BACKEND_CORS_ORIGINS')
print(f"  BACKEND_CORS_ORIGINS: {cors_origins}")

# 检查Pydantic配置
print("\nPydantic配置检查:")
try:
    # 更改工作目录到后端目录
    os.chdir(backend_path)
    print(f"已切换到后端目录: {os.getcwd()}")
    
    from app.core.config import settings
    print(f"  BACKEND_CORS_ORIGINS: {settings.BACKEND_CORS_ORIGINS}")
    
    # 检查是否包含我们需要的地址
    expected_origin = "http://192.168.10.35:3000"
    cors_origins_list = [str(url).rstrip('/') for url in settings.BACKEND_CORS_ORIGINS]
    print(f"  CORS源列表(去除末尾斜杠): {cors_origins_list}")
    
    if expected_origin in cors_origins_list:
        print(f"  ✓ 配置中包含 {expected_origin}")
    else:
        print(f"  ✗ 配置中不包含 {expected_origin}")
        # 显示所有配置信息用于调试
        print(f"  完整配置信息:")
        for i, url in enumerate(settings.BACKEND_CORS_ORIGINS):
            print(f"    [{i}] {url} (str: {str(url)})")
        
except Exception as e:
    print(f"配置加载失败: {e}")
    import traceback
    traceback.print_exc()

print("\n系统环境变量检查:")
import subprocess
result = subprocess.run(["set"], shell=True, capture_output=True, text=True)
if result.returncode == 0:
    env_lines = result.stdout.split('\n')
    for line in env_lines:
        if 'BACKEND_CORS_ORIGINS' in line:
            print(f"  {line}")