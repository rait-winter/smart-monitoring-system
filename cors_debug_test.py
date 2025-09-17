#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORS调试测试脚本
用于诊断前端与后端之间的CORS配置问题
"""

import os
import json
import requests
from dotenv import load_dotenv

def load_env_config():
    """加载环境配置"""
    # 尝试加载环境变量文件
    env_files = [".env", ".env.development", "backend/.env", "backend/.env.development"]
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"✅ 已加载环境文件: {env_file}")
            break
    else:
        print("⚠️ 未找到环境配置文件")

def test_cors_preflight():
    """测试CORS预检请求"""
    backend_url = os.getenv("VITE_API_BASE_URL", "http://192.168.10.35:8000")
    test_endpoint = f"{backend_url}/api/v1/prometheus/test"
    
    print(f"📡 测试CORS预检请求")
    print(f"   后端地址: {backend_url}")
    print(f"   测试端点: {test_endpoint}")
    print(f"   前端地址: http://192.168.10.35:3000")
    
    # 发送OPTIONS预检请求
    headers = {
        "Origin": "http://192.168.10.35:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.options(test_endpoint, headers=headers, timeout=10)
        print(f"\n📋 预检请求响应:")
        print(f"   状态码: {response.status_code}")
        print(f"   响应头:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower():
                print(f"     {key}: {value}")
        
        # 检查关键CORS头
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"\n🔍 CORS头检查:")
        for header, value in cors_headers.items():
            if value:
                print(f"   ✅ {header}: {value}")
            else:
                print(f"   ❌ {header}: 未设置")
                
        return response.headers
        
    except Exception as e:
        print(f"❌ 预检请求失败: {e}")
        return None

def test_actual_request():
    """测试实际POST请求"""
    backend_url = os.getenv("VITE_API_BASE_URL", "http://192.168.10.35:8000")
    test_endpoint = f"{backend_url}/api/v1/prometheus/test"
    
    print(f"\n📡 测试实际POST请求")
    print(f"   端点: {test_endpoint}")
    
    # 测试数据
    test_data = {
        "url": "http://localhost:9090",
        "timeout": 30
    }
    
    headers = {
        "Origin": "http://192.168.10.35:3000",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(test_endpoint, json=test_data, headers=headers, timeout=10)
        print(f"\n📋 实际请求响应:")
        print(f"   状态码: {response.status_code}")
        print(f"   响应头:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower():
                print(f"     {key}: {value}")
        
        try:
            response_data = response.json()
            print(f"   响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"   响应内容: {response.text[:200]}...")
            
        return response.headers
        
    except Exception as e:
        print(f"❌ 实际请求失败: {e}")
        return None

def check_env_config():
    """检查环境配置"""
    print("\n🔧 环境配置检查:")
    
    cors_origins = os.getenv("BACKEND_CORS_ORIGINS")
    print(f"   BACKEND_CORS_ORIGINS: {cors_origins}")
    
    api_base_url = os.getenv("VITE_API_BASE_URL")
    print(f"   VITE_API_BASE_URL: {api_base_url}")
    
    # 检查是否包含前端地址
    frontend_url = "http://192.168.10.35:3000"
    if cors_origins and frontend_url in cors_origins:
        print(f"   ✅ CORS配置包含前端地址")
    else:
        print(f"   ❌ CORS配置可能缺失前端地址")

def main():
    """主函数"""
    print("🚀 CORS调试测试工具")
    print("=" * 50)
    
    # 加载环境配置
    load_env_config()
    
    # 检查环境配置
    check_env_config()
    
    # 测试CORS预检请求
    print("\n" + "=" * 50)
    preflight_headers = test_cors_preflight()
    
    # 测试实际请求
    print("\n" + "=" * 50)
    actual_headers = test_actual_request()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成")

if __name__ == "__main__":
    main()