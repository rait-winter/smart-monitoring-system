#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证数据库配置
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

# 确保在导入其他模块之前加载环境变量
from dotenv import load_dotenv

print("当前工作目录:", os.getcwd())

# 加载.env文件
if os.path.exists('.env'):
    print("✓ 加载.env文件")
    load_dotenv('.env', override=True)
else:
    print("✗ 未找到.env文件")

print("环境变量 DATABASE_URL:", os.getenv('DATABASE_URL'))

# 导入配置
try:
    from app.core.config import settings
    print("Pydantic配置 DATABASE_URL:", settings.DATABASE_URL)
    
    # 解析数据库URL信息
    import urllib.parse
    parsed = urllib.parse.urlparse(settings.DATABASE_URL)
    print("\n数据库连接信息:")
    print(f"  数据库类型: {parsed.scheme}")
    print(f"  主机: {parsed.hostname}")
    print(f"  端口: {parsed.port}")
    print(f"  数据库名: {parsed.path[1:] if parsed.path.startswith('/') else parsed.path}")
    print(f"  用户名: {parsed.username}")
    
    # 验证是否与您提供的信息匹配
    expected_host = "192.168.233.133"
    expected_port = 30199
    expected_user = "postgres"
    expected_db = "smart_monitoring"
    
    if (parsed.hostname == expected_host and 
        parsed.port == expected_port and 
        parsed.username == expected_user and 
        (parsed.path[1:] if parsed.path.startswith('/') else parsed.path) == expected_db):
        print("\n✓ 数据库配置验证通过")
    else:
        print("\n✗ 数据库配置验证失败")
        print(f"  期望主机: {expected_host}, 实际: {parsed.hostname}")
        print(f"  期望端口: {expected_port}, 实际: {parsed.port}")
        print(f"  期望用户: {expected_user}, 实际: {parsed.username}")
        print(f"  期望数据库: {expected_db}, 实际: {parsed.path[1:] if parsed.path.startswith('/') else parsed.path}")
        
except Exception as e:
    print(f"导入配置时出错: {e}")
    import traceback
    traceback.print_exc()