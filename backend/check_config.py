#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查配置加载
"""

import os

print("当前工作目录:", os.getcwd())
print("环境变量文件:", os.listdir('.'))

# 检查环境变量
print("\n环境变量检查:")
print("ENVIRONMENT:", os.environ.get('ENVIRONMENT', '未设置'))
print("DATABASE_URL:", os.environ.get('DATABASE_URL', '未设置'))

# 检查配置文件
try:
    from app.core.config import settings
    print("\n配置加载结果:")
    print("应用名称:", settings.APP_NAME)
    print("环境:", settings.ENVIRONMENT)
    print("数据库URL:", settings.DATABASE_URL)
    print("是否为开发环境:", settings.is_development)
except Exception as e:
    print(f"\n配置加载失败: {e}")
    import traceback
    traceback.print_exc()