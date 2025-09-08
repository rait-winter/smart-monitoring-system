#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试配置加载过程
"""

import os
from dotenv import load_dotenv

# 手动加载环境变量
print("手动加载环境变量...")
env_files = [".env", ".env.development", "../.env", "../.env.development"]
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"加载环境文件: {env_file}")
        load_dotenv(env_file)
        break

print("环境变量检查:")
print(f"  DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT')}")

# 现在测试Pydantic配置
print("\n测试Pydantic配置加载...")
try:
    from app.core.config import Settings
    
    # 创建配置实例
    settings = Settings()
    print(f"配置实例 DATABASE_URL: {settings.DATABASE_URL}")
    print(f"配置实例 ENVIRONMENT: {settings.ENVIRONMENT}")
    
except Exception as e:
    print(f"配置加载失败: {e}")
    import traceback
    traceback.print_exc()