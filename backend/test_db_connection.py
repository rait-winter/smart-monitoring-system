#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试数据库连接
"""

import asyncio
import sys
import os

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

try:
    from app.core.config import settings
    print(f"配置 DATABASE_URL: {settings.DATABASE_URL}")
    print(f"配置 ENVIRONMENT: {settings.ENVIRONMENT}")
    
    from app.core.database import engine
    print(f"引擎 URL: {engine.url}")
    
    async def test_connection():
        try:
            async with engine.begin() as conn:
                print("✅ 数据库连接成功!")
                # 使用正确的SQLAlchemy语法
                from sqlalchemy import text
                result = await conn.execute(text("SELECT 1"))
                print(f"查询结果: {result.scalar()}")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_connection())
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()