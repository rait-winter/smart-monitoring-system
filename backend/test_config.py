#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试配置加载
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings
    print("✅ 配置加载成功!")
    print(f"应用名称: {settings.APP_NAME}")
    print(f"环境: {settings.ENVIRONMENT}")
    print(f"调试模式: {settings.DEBUG}")
    print(f"数据库URL: {settings.DATABASE_URL}")
    
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    import traceback
    traceback.print_exc()