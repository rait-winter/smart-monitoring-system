#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能监控预警系统 - PostgreSQL数据库初始化脚本
用于创建数据库表结构和初始数据
"""

import asyncio
import asyncpg
import os
from pathlib import Path

# 数据库连接配置
DB_CONFIG = {
    'host': '192.168.233.133',
    'port': 30199,
    'user': 'postgres',
    'password': 'zalando',
    'database': 'smart_monitoring'
}

async def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    try:
        # 先连接到默认的postgres数据库
        conn = await asyncpg.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'  # 连接到默认数据库
        )
        
        # 检查数据库是否存在
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            DB_CONFIG['database']
        )
        
        if not exists:
            print(f"创建数据库: {DB_CONFIG['database']}")
            await conn.execute(f'CREATE DATABASE "{DB_CONFIG["database"]}"')
            print("数据库创建成功")
        else:
            print(f"数据库 {DB_CONFIG['database']} 已存在")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        return False

async def init_database():
    """初始化数据库表结构"""
    try:
        # 连接到目标数据库
        conn = await asyncpg.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        
        # 读取SQL初始化脚本
        sql_file = Path(__file__).parent / "init_db.sql"
        if not sql_file.exists():
            print(f"SQL文件不存在: {sql_file}")
            return False
            
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 执行SQL脚本
        print("开始执行数据库初始化脚本...")
        await conn.execute(sql_script)
        print("数据库初始化完成")
        
        # 验证表创建
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print("\n已创建的表:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("智能监控预警系统 - 数据库初始化工具")
    print("=" * 50)
    print(f"数据库地址: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"数据库名称: {DB_CONFIG['database']}")
    print(f"用户名: {DB_CONFIG['user']}")
    print("=" * 50)
    
    # 创建数据库
    print("步骤1: 检查并创建数据库...")
    if not await create_database_if_not_exists():
        print("创建数据库失败")
        return
    
    # 初始化表结构
    print("\n步骤2: 初始化数据库表结构...")
    if await init_database():
        print("\n✓ 数据库初始化成功完成")
        print("\n您可以使用以下信息连接到数据库:")
        print(f"  主机: {DB_CONFIG['host']}")
        print(f"  端口: {DB_CONFIG['port']}")
        print(f"  数据库: {DB_CONFIG['database']}")
        print(f"  用户名: {DB_CONFIG['user']}")
        print(f"  密码: {DB_CONFIG['password']}")
    else:
        print("\n✗ 数据库初始化失败")

if __name__ == "__main__":
    asyncio.run(main())