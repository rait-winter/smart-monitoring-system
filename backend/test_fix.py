#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修复后的规则引擎
"""

try:
    from app.core.config import settings
    print("✅ 配置加载成功!")
    print(f"应用名称: {settings.APP_NAME}")
    print(f"环境: {settings.ENVIRONMENT}")
    print(f"调试模式: {settings.DEBUG}")
    
    # 测试规则引擎导入
    from app.services.rule_engine import RuleEngine
    print("✅ 规则引擎导入成功!")
    
    # 创建规则引擎实例
    engine = RuleEngine()
    print("✅ 规则引擎实例创建成功!")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()