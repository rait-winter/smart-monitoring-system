#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试配置保存功能
"""
import asyncio
import sys
import os
sys.path.append('.')

async def test_config_save():
    try:
        from app.services.config_db_service import ConfigDBService
        
        service = ConfigDBService()
        config_data = {
            'name': 'test-prod-simple',
            'url': 'http://192.168.233.137:30090',
            'enabled': True,
            'timeout': 30000,
            'scrapeInterval': '15s',
            'evaluationInterval': '15s'
        }
        
        print('📝 开始测试配置保存...')
        result = await service.save_prometheus_config(config_data)
        print('保存结果:', result)
        
        if result.get('success'):
            print('✅ 配置保存成功!')
            config_id = result.get('id')
            if config_id:
                print(f'配置ID: {config_id}')
        else:
            print('❌ 配置保存失败:', result.get('message'))
        
        # 测试获取默认配置
        print('📖 测试获取默认配置...')
        default_config = await service.get_default_prometheus_config()
        if default_config:
            print('默认配置名称:', default_config.get('name'))
            print('默认配置URL:', default_config.get('url'))
        else:
            print('❌ 未找到默认配置')
        
    except Exception as e:
        print('❌ 测试失败:', str(e))
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_config_save())
