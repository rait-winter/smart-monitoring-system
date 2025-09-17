#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Prometheus配置保存功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.services.config_db_service import config_db_service
from backend.app.core.database import init_db

async def test_config_save():
    """测试配置保存功能"""
    print("开始测试Prometheus配置保存功能...")
    
    try:
        # 初始化数据库连接
        await init_db()
        print("✅ 数据库连接初始化成功")
        
        # 测试配置数据
        test_config = {
            "name": "测试配置",
            "url": "http://localhost:9090",
            "username": "admin",
            "password": "password123",
            "timeout": 30,
            "scrapeInterval": "15s",
            "evaluationInterval": "15s",
            "max_retries": 3,
            "enabled": True
        }
        
        print(f"📝 测试配置数据: {test_config}")
        
        # 保存配置
        result = await config_db_service.save_prometheus_config(test_config)
        print(f"✅ 配置保存成功: {result}")
        
        # 获取配置验证
        saved_config = await config_db_service.get_default_prometheus_config()
        print(f"📖 获取保存的配置: {saved_config}")
        
        # 验证字段映射
        if saved_config:
            print("🔍 字段映射验证:")
            print(f"  - URL: {saved_config.get('url')}")
            print(f"  - 采集间隔: {saved_config.get('scrape_interval')}")
            print(f"  - 评估间隔: {saved_config.get('evaluation_interval')}")
            print(f"  - 启用状态: {saved_config.get('is_enabled')}")
        
        print("🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_config_save())

