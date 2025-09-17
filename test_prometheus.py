import requests
import json

# 测试Prometheus连接
url = "http://localhost:8000/api/v1/system/prometheus/test"
payload = {
    "url": "http://192.168.233.137:30090"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")