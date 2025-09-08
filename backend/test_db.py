#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试数据库配置
"""

try:
    from app.core.config import settings
    print("✅ 配置加载成功!")
    print(f"应用名称: {settings.APP_NAME}")
    print(f"环境: {settings.ENVIRONMENT}")
    print(f"调试模式: {settings.DEBUG}")
    print(f"数据库URL: {settings.DATABASE_URL}")
    
    # 测试数据库连接
    from app.core.database import engine
    print("✅ 数据库引擎创建成功!")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()