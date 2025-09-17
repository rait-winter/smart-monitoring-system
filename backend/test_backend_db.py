#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能监控预警系统 - 后端数据库配置测试脚本
用于验证后端配置文件中的数据库连接配置
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    # 导入后端配置
    from app.core.config import settings
    
    print("智能监控预警系统 - 后端数据库配置测试")
    print("=" * 50)
    print(f"环境: {settings.ENVIRONMENT}")
    print(f"调试模式: {settings.DEBUG}")
    print("=" * 50)
    
    # 显示数据库配置
    print("数据库配置信息:")
    print(f"  数据库URL: {settings.DATABASE_URL}")
    
    # 解析数据库URL信息
    import urllib.parse
    parsed = urllib.parse.urlparse(settings.DATABASE_URL)
    print(f"  数据库类型: {parsed.scheme}")
    print(f"  主机: {parsed.hostname}")
    print(f"  端口: {parsed.port}")
    print(f"  数据库名: {parsed.path[1:] if parsed.path.startswith('/') else parsed.path}")
    print(f"  用户名: {parsed.username}")
    
    # 测试数据库连接
    print("\n测试数据库连接...")
    
    # 使用SQLAlchemy异步引擎测试连接
    from app.core.database import engine
    from sqlalchemy import text
    
    import asyncio
    
    async def test_connection():
        try:
            # 测试连接
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"✓ 数据库连接成功")
                print(f"  数据库版本: {version}")
                
                # 测试查询用户表
                result = await conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                print(f"✓ 用户表记录数: {count}")
                
                # 测试查询巡检规则表
                result = await conn.execute(text("SELECT COUNT(*) FROM inspection_rules"))
                count = result.scalar()
                print(f"✓ 巡检规则表记录数: {count}")
                
            return True
        except Exception as e:
            print(f"✗ 数据库连接测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # 运行异步测试
    if asyncio.run(test_connection()):
        print("\n✓ 后端数据库配置测试通过")
        print("\n数据库已准备就绪，可以启动后端服务")
    else:
        print("\n✗ 后端数据库配置测试失败")
        
except Exception as e:
    print(f"导入后端配置时出错: {e}")
    import traceback
    traceback.print_exc()