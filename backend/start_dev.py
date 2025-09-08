#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开发环境启动脚本
"""

import os
import sys

# 设置环境变量
os.environ["ENVIRONMENT"] = "development"

print("设置环境变量:")
print("ENVIRONMENT:", os.environ.get("ENVIRONMENT"))

# 导入并测试配置
try:
    from app.core.config import settings
    print("\n配置加载成功:")
    print("应用名称:", settings.APP_NAME)
    print("环境:", settings.ENVIRONMENT)
    print("数据库URL:", settings.DATABASE_URL)
    
    # 测试数据库连接
    from app.core.database import engine
    print("\n数据库引擎创建成功!")
    print("数据库URL:", engine.url)
    
except Exception as e:
    print(f"\n配置加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ 开发环境配置测试完成!")