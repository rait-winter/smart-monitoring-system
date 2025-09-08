#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整调试配置加载过程
"""

import os
from dotenv import load_dotenv

print("=== 环境变量加载阶段 ===")
# 手动加载环境变量
env_files = [".env", ".env.development", "../.env", "../.env.development"]
loaded_env = None
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"加载环境文件: {env_file}")
        load_dotenv(env_file)
        loaded_env = env_file
        break

print("环境变量检查:")
print(f"  DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT')}")

print("\n=== Pydantic配置加载阶段 ===")
try:
    # 在导入配置之前检查环境变量
    print("导入配置模块前的环境变量:")
    print(f"  DATABASE_URL: {os.getenv('DATABASE_URL')}")
    print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT')}")
    
    from app.core.config import Settings
    
    print("创建配置实例...")
    settings = Settings()
    print(f"配置实例 DATABASE_URL: {settings.DATABASE_URL}")
    print(f"配置实例 ENVIRONMENT: {settings.ENVIRONMENT}")
    
    print("\n=== 全局设置检查 ===")
    from app.core.config import settings as global_settings
    print(f"全局设置 DATABASE_URL: {global_settings.DATABASE_URL}")
    print(f"全局设置 ENVIRONMENT: {global_settings.ENVIRONMENT}")
    
except Exception as e:
    print(f"配置加载失败: {e}")
    import traceback
    traceback.print_exc()