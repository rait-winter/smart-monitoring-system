#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本

用于初始化数据库表结构和基础数据

使用方法:
    python scripts/init-db.py
"""

import sys
import os
import asyncio

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import init_db, drop_db
from app.core.config import settings

async def main():
    """主函数"""
    print("开始初始化数据库...")
    
    try:
        # 初始化数据库表
        await init_db()
        print("✅ 数据库初始化完成")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())