#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境变量配置
"""

import os
import sys

# 确保在导入其他模块之前加载环境变量
from dotenv import load_dotenv

# 尝试加载环境变量文件
env_files = [".env", ".env.development", "../.env", "../.env.development"]
print("加载环境变量文件:")
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"  ✓ 加载环境文件: {env_file}")
        load_dotenv(env_file, override=True)
    else:
        print(f"  ✗ 未找到环境文件: {env_file}")

print(f"\n环境变量 DATABASE_URL: {os.getenv('DATABASE_URL')}")

# 现在导入配置
try:
    from app.core.config import settings
    print(f"\nPydantic配置 DATABASE_URL: {settings.DATABASE_URL}")
except Exception as e:
    print(f"导入配置时出错: {e}")
    import traceback
    traceback.print_exc()