from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Any
import httpx
from urllib.parse import urljoin

app = FastAPI()

@app.post("/prometheus/test")
async def test_prometheus_connection(config: Dict[str, Any] = Body(...)):
    """测试Prometheus连接"""
    try:
        # 获取URL
        prometheus_url = config.get("url", "http://localhost:9090")
        
        # 创建HTTP客户端
        async with httpx.AsyncClient() as client:
            # 测试健康检查端点
            health_url = urljoin(prometheus_url.rstrip('/'), "/-/healthy")
            response = await client.get(health_url, timeout=5.0)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Prometheus连接测试成功",
                    "data": {"healthy": True}
                }
            else:
                return {
                    "success": False,
                    "message": "Prometheus连接测试失败",
                    "data": {"healthy": False, "status_code": response.status_code}
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"Prometheus连接测试失败: {str(e)}",
            "data": {"healthy": False, "error": str(e)}
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)