#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能监控预警系统 - 数据库连接测试脚本
用于验证数据库连接和表结构
"""

import asyncio
import asyncpg
import os

# 数据库连接配置
DB_CONFIG = {
    'host': '192.168.233.133',
    'port': 30199,
    'user': 'postgres',
    'password': 'zalando',
    'database': 'smart_monitoring'
}

async def test_database_connection():
    """测试数据库连接"""
    try:
        # 连接到数据库
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✓ 数据库连接成功")
        
        # 测试查询用户表
        users = await conn.fetch("SELECT COUNT(*) as count FROM users")
        print(f"✓ 用户表记录数: {users[0]['count']}")
        
        # 测试查询巡检规则表
        rules = await conn.fetch("SELECT COUNT(*) as count FROM inspection_rules")
        print(f"✓ 巡检规则表记录数: {rules[0]['count']}")
        
        # 测试查询指标元数据表
        metrics = await conn.fetch("SELECT COUNT(*) as count FROM metrics_metadata")
        print(f"✓ 指标元数据表记录数: {metrics[0]['count']}")
        
        # 显示表结构信息
        print("\n数据库表结构信息:")
        tables = await conn.fetch("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        for table in tables:
            print(f"  - {table['table_name']} ({table['column_count']} 列)")
        
        # 显示初始数据
        print("\n初始数据检查:")
        
        # 检查用户数据
        admin_user = await conn.fetchrow("SELECT username, email, role FROM users WHERE username = 'admin'")
        if admin_user:
            print(f"  ✓ 管理员用户: {admin_user['username']} ({admin_user['email']}) - {admin_user['role']}")
        
        # 检查巡检规则数据
        rules_count = await conn.fetchval("SELECT COUNT(*) FROM inspection_rules")
        print(f"  ✓ 巡检规则数量: {rules_count}")
        
        # 检查指标元数据
        metrics_count = await conn.fetchval("SELECT COUNT(*) FROM metrics_metadata")
        print(f"  ✓ 指标元数据数量: {metrics_count}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("智能监控预警系统 - 数据库连接测试")
    print("=" * 40)
    print(f"数据库地址: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"数据库名称: {DB_CONFIG['database']}")
    print("=" * 40)
    
    if await test_database_connection():
        print("\n✓ 所有数据库测试通过")
    else:
        print("\n✗ 数据库测试失败")

if __name__ == "__main__":
    asyncio.run(main())