#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试配置
"""

import os

# 确保在导入其他模块之前加载环境变量
from dotenv import load_dotenv

# 尝试加载环境变量文件
print("当前工作目录:", os.getcwd())
print("环境变量 DATABASE_URL:", os.getenv('DATABASE_URL'))

# 加载.env文件
if os.path.exists('.env'):
    print("加载.env文件")
    load_dotenv('.env', override=True)
else:
    print("未找到.env文件")

print("加载后 DATABASE_URL:", os.getenv('DATABASE_URL'))

# 导入配置
from app.core.config import settings
print("Pydantic配置 DATABASE_URL:", settings.DATABASE_URL)