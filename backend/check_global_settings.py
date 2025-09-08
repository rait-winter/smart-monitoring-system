#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查全局设置实例
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
from dotenv import load_dotenv
env_files = [".env", ".env.development", "../.env", "../.env.development"]
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"加载环境文件: {env_file}")
        load_dotenv(env_file)
        break

print("环境变量检查:")
print(f"  DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT')}")

# 检查全局设置
from app.core.config import settings
print(f"全局设置 DATABASE_URL: {settings.DATABASE_URL}")
print(f"全局设置 ENVIRONMENT: {settings.ENVIRONMENT}")

# 检查数据库引擎
from app.core.database import engine
print(f"数据库引擎 URL: {engine.url}")