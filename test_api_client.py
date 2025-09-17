import requests
import json

def test_prometheus_api():
    """测试Prometheus API端点"""
    url = "http://localhost:8001/prometheus/test"
    payload = {
        "url": "http://192.168.233.137:30090"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("正在测试Prometheus API端点...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    success = test_prometheus_api()
    if success:
        print("✓ Prometheus API测试成功")
    else:
        print("✗ Prometheus API测试失败")