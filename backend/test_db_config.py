#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库配置
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

# 确保在导入其他模块之前加载环境变量
from dotenv import load_dotenv

# 尝试加载环境变量文件
print("当前工作目录:", os.getcwd())
env_files = [".env", ".env.development", "../.env", "../.env.development"]
print("加载环境变量文件:")
for env_file in env_files:
    if os.path.exists(env_file):
        print(f"  ✓ 加载环境文件: {env_file}")
        load_dotenv(env_file, override=True)
    else:
        print(f"  ✗ 未找到环境文件: {env_file}")

print(f"\n环境变量 DATABASE_URL: {os.getenv('DATABASE_URL')}")

# 清除缓存并重新导入配置
try:
    import importlib
    import app.core.config
    
    # 清除模块缓存
    if 'app.core.config' in sys.modules:
        del sys.modules['app.core.config']
    
    # 重新导入
    from app.core.config import Settings
    
    # 创建新的配置实例
    settings = Settings()
    print(f"\nPydantic配置 DATABASE_URL: {settings.DATABASE_URL}")
    
    # 解析数据库URL信息
    import urllib.parse
    parsed = urllib.parse.urlparse(settings.DATABASE_URL)
    print(f"\n数据库连接信息:")
    print(f"  数据库类型: {parsed.scheme}")
    print(f"  主机: {parsed.hostname}")
    print(f"  端口: {parsed.port}")
    print(f"  数据库名: {parsed.path[1:] if parsed.path.startswith('/') else parsed.path}")
    print(f"  用户名: {parsed.username}")
    
except Exception as e:
    print(f"导入配置时出错: {e}")
    import traceback
    traceback.print_exc()