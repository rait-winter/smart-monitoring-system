#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查环境变量加载
"""

import os
from dotenv import load_dotenv

# 尝试加载.env文件
env_files = [".env", ".env.development", "../.env", "../.env.development"]
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"找到环境文件: {env_file}")
        load_dotenv(env_file)
        break
else:
    print("未找到任何环境文件")

# 检查关键环境变量
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
print("ENVIRONMENT:", os.getenv("ENVIRONMENT"))
print("DEBUG:", os.getenv("DEBUG"))