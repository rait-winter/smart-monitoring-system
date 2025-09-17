#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prometheus连接测试脚本 - 验证修复后的配置
"""

import requests
import json

def test_prometheus_connection():
    """测试Prometheus连接API端点"""
    # 使用修复后的API端点
    url = "http://192.168.10.35:8000/api/v1/prometheus/test"
    
    # 测试配置
    payload = {
        "url": "http://localhost:9090"  # 使用本地Prometheus
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("正在测试Prometheus连接...")
        print(f"请求URL: {url}")
        print(f"请求数据: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ Prometheus连接测试成功")
                return True
            else:
                print("✗ Prometheus连接测试失败")
                print(f"错误信息: {result.get('message')}")
                return False
        else:
            print(f"✗ HTTP请求失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到后端服务，请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cors():
    """测试CORS配置"""
    url = "http://192.168.10.35:8000/api/v1/prometheus/test"
    
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://192.168.10.35:3000"  # 前端地址
    }
    
    try:
        print("\n正在测试CORS配置...")
        response = requests.options(url, headers=headers, timeout=10)
        
        print(f"CORS预检请求状态码: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
        print(f"Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'NOT SET')}")
        print(f"Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'NOT SET')}")
        
        return response.status_code in [200, 204]
        
    except Exception as e:
        print(f"CORS测试错误: {e}")
        return False

if __name__ == "__main__":
    print("智能监控预警系统 - Prometheus连接修复验证")
    print("=" * 50)
    
    # 测试CORS配置
    cors_ok = test_cors()
    
    # 测试Prometheus连接
    prometheus_ok = test_prometheus_connection()
    
    print("\n" + "=" * 50)
    print("测试结果:")
    print(f"CORS配置: {'✓ 通过' if cors_ok else '✗ 失败'}")
    print(f"Prometheus连接: {'✓ 通过' if prometheus_ok else '✗ 失败'}")
    
    if cors_ok and prometheus_ok:
        print("\n🎉 所有测试通过，问题已修复!")
    else:
        print("\n❌ 部分测试失败，请检查配置")