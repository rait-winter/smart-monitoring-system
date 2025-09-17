#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查环境变量配置
"""

import os
from dotenv import load_dotenv

# 尝试加载环境变量文件
env_files = [".env", ".env.development", "../.env", "../.env.development"]
print("检查环境变量文件:")
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"  ✓ 找到环境文件: {env_file}")
        load_dotenv(env_file)
    else:
        print(f"  ✗ 未找到环境文件: {env_file}")

print("\n数据库相关环境变量:")
print(f"  DATABASE_URL: {os.getenv('DATABASE_URL', '未设置')}")

# 检查PostgreSQL相关环境变量
postgres_vars = ['POSTGRES_SERVER', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB', 'POSTGRES_PORT']
for var in postgres_vars:
    value = os.getenv(var, '未设置')
    print(f"  {var}: {value}")

print("\n其他重要环境变量:")
important_vars = ['ENVIRONMENT', 'DEBUG', 'HOST', 'PORT']
for var in important_vars:
    value = os.getenv(var, '未设置')
    print(f"  {var}: {value}")