import requests
import json

def test_prometheus_connection():
    """测试Prometheus连接API端点"""
    url = "http://localhost:8000/api/v1/system/prometheus/test"
    payload = {
        "url": "http://192.168.233.137:30090"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("正在测试Prometheus连接...")
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到后端服务，请确保服务正在运行")
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    success = test_prometheus_connection()
    if success:
        print("✓ Prometheus连接测试成功")
    else:
        print("✗ Prometheus连接测试失败")