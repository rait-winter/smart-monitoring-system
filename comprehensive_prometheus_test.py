#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合Prometheus连接测试
测试前端配置的Prometheus地址是否可以正常连接
"""

import requests
import json
import time

def test_direct_prometheus_connection(prometheus_url):
    """直接测试Prometheus连接"""
    print(f"\n1. 直接测试Prometheus连接: {prometheus_url}")
    
    try:
        # 测试健康检查端点
        health_url = f"{prometheus_url.rstrip('/')}/-/healthy"
        print(f"   健康检查URL: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✓ Prometheus直接连接成功")
            return True
        else:
            print(f"   ✗ Prometheus直接连接失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ✗ Prometheus直接连接异常: {e}")
        return False

def test_backend_prometheus_api(backend_url, prometheus_url):
    """测试后端Prometheus API"""
    print(f"\n2. 测试后端Prometheus API: {backend_url}")
    
    try:
        # 测试后端Prometheus测试端点
        test_url = f"{backend_url.rstrip('/')}/api/v1/prometheus/test"
        print(f"   测试API URL: {test_url}")
        
        payload = {
            "url": prometheus_url
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(test_url, data=json.dumps(payload), headers=headers, timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("   ✓ 后端Prometheus API测试成功")
                return True
            else:
                print(f"   ✗ 后端Prometheus API测试失败: {result.get('message')}")
                return False
        else:
            print(f"   ✗ 后端Prometheus API请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ✗ 后端Prometheus API异常: {e}")
        return False

def test_cors_configuration(backend_url):
    """测试CORS配置"""
    print(f"\n3. 测试CORS配置: {backend_url}")
    
    try:
        test_url = f"{backend_url.rstrip('/')}/api/v1/prometheus/test"
        
        # 发送CORS预检请求
        headers = {
            "Origin": "http://192.168.10.35:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.options(test_url, headers=headers, timeout=10)
        print(f"   预检请求状态码: {response.status_code}")
        
        # 检查关键CORS响应头
        aca_origin = response.headers.get('Access-Control-Allow-Origin', 'NOT SET')
        aca_methods = response.headers.get('Access-Control-Allow-Methods', 'NOT SET')
        aca_headers = response.headers.get('Access-Control-Allow-Headers', 'NOT SET')
        
        print(f"   Access-Control-Allow-Origin: {aca_origin}")
        print(f"   Access-Control-Allow-Methods: {aca_methods}")
        print(f"   Access-Control-Allow-Headers: {aca_headers}")
        
        if aca_origin != 'NOT SET' and '192.168.10.35:3000' in aca_origin:
            print("   ✓ CORS配置正确")
            return True
        else:
            print("   ✗ CORS配置有问题")
            return False
            
    except Exception as e:
        print(f"   ✗ CORS测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("智能监控预警系统 - 综合Prometheus连接测试")
    print("=" * 50)
    
    # 配置信息
    backend_url = "http://192.168.10.35:8000"
    prometheus_url = "http://localhost:9090"  # 这应该与前端配置的地址一致
    
    print(f"后端地址: {backend_url}")
    print(f"Prometheus地址: {prometheus_url}")
    
    # 执行所有测试
    start_time = time.time()
    
    direct_ok = test_direct_prometheus_connection(prometheus_url)
    backend_ok = test_backend_prometheus_api(backend_url, prometheus_url)
    cors_ok = test_cors_configuration(backend_url)
    
    end_time = time.time()
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"  直接Prometheus连接: {'✓ 通过' if direct_ok else '✗ 失败'}")
    print(f"  后端Prometheus API: {'✓ 通过' if backend_ok else '✗ 失败'}")
    print(f"  CORS配置: {'✓ 通过' if cors_ok else '✗ 失败'}")
    
    if direct_ok and backend_ok and cors_ok:
        print("\n🎉 所有测试通过！Prometheus连接配置正确。")
    else:
        print("\n❌ 部分测试失败，请根据上面的错误信息进行修复。")
        
        # 提供修复建议
        if not direct_ok:
            print("\n修复建议:")
            print("1. 检查Prometheus服务是否正在运行")
            print("2. 确认Prometheus地址配置正确")
            print("3. 检查网络连接和防火墙设置")
            
        if not backend_ok:
            print("\n修复建议:")
            print("1. 检查后端服务是否正常运行")
            print("2. 确认后端Prometheus API端点实现正确")
            print("3. 查看后端日志获取更多信息")
            
        if not cors_ok:
            print("\n修复建议:")
            print("1. 检查后端.env文件中的BACKEND_CORS_ORIGINS配置")
            print("2. 确保包含'http://192.168.10.35:3000'")
            print("3. 重启后端服务以应用新的CORS配置")
    
    print(f"\n测试耗时: {end_time - start_time:.2f}秒")

if __name__ == "__main__":
    main()