#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CORS请求
"""

import requests

def test_cors_preflight():
    """测试CORS预检请求"""
    url = "http://192.168.10.35:8000/prometheus/test"
    
    headers = {
        "Origin": "http://192.168.10.35:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        print(f"发送CORS预检请求到: {url}")
        response = requests.options(url, headers=headers, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print("响应头:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
            
        # 检查关键的CORS头
        aca_origin = response.headers.get('Access-Control-Allow-Origin', 'NOT SET')
        aca_methods = response.headers.get('Access-Control-Allow-Methods', 'NOT SET')
        aca_headers = response.headers.get('Access-Control-Allow-Headers', 'NOT SET')
        
        print(f"\nCORS响应头检查:")
        print(f"  Access-Control-Allow-Origin: {aca_origin}")
        print(f"  Access-Control-Allow-Methods: {aca_methods}")
        print(f"  Access-Control-Allow-Headers: {aca_headers}")
        
        if aca_origin != 'NOT SET':
            print("✓ CORS预检请求成功")
            return True
        else:
            print("✗ CORS预检请求失败")
            return False
            
    except Exception as e:
        print(f"请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("CORS预检请求测试")
    print("=" * 30)
    test_cors_preflight()