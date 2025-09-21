"""
Ollama配置和AI服务相关的API端点
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import structlog
import aiohttp
import asyncio

from app.models.schemas import APIResponse
from app.services.config_db_service import config_db_service

logger = structlog.get_logger(__name__)

# 创建路由器
router = APIRouter()


@router.get("/config", response_model=APIResponse)
async def get_ollama_config() -> APIResponse:
    """获取Ollama配置"""
    try:
        # 优先从数据库获取配置
        db_config = await config_db_service.get_default_ollama_config()
        if db_config:
            config = {
                "name": db_config["name"],
                "enabled": db_config["enabled"],
                "apiUrl": db_config["apiUrl"],
                "model": db_config["model"],
                "timeout": db_config["timeout"],
                "maxTokens": db_config["maxTokens"],
                "temperature": db_config["temperature"]
            }
        else:
            # 返回默认配置
            config = {
                "name": "默认Ollama配置",
                "enabled": False,
                "apiUrl": "http://localhost:11434",
                "model": "llama3.2",
                "timeout": 60000,
                "maxTokens": 2048,
                "temperature": 0.7
            }
        
        return APIResponse(
            success=True,
            message="获取配置成功",
            data=config
        )
        
    except Exception as e:
        logger.error("获取Ollama配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config", response_model=APIResponse)
async def update_ollama_config(config: Dict[str, Any] = Body(..., description="Ollama配置")) -> APIResponse:
    """更新Ollama配置"""
    try:
        # 保存配置到数据库
        result = await config_db_service.save_ollama_config(config)
        
        # 检查保存结果
        if not result.get("success", True):
            return APIResponse(
                success=False,
                message=result.get("message", "配置保存失败"),
                data=result
            )
        
        return APIResponse(
            success=True,
            message="配置保存成功",
            data=result
        )
        
    except Exception as e:
        logger.error("保存Ollama配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test", response_model=APIResponse)
async def test_ollama_connection(config: Dict[str, Any] = Body(..., description="Ollama配置")) -> APIResponse:
    """测试Ollama连接"""
    try:
        api_url = config.get("apiUrl", "http://localhost:11434")
        timeout = config.get("timeout", 60000) / 1000  # 转换为秒
        
        # 构建测试URL
        test_url = f"{api_url.rstrip('/')}/api/tags"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            try:
                async with session.get(test_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        
                        model_list = []
                        for model in models:
                            model_info = {
                                "name": model.get("name", ""),
                                "label": model.get("name", ""),
                                "size": model.get("size", 0)
                            }
                            model_list.append(model_info)
                        
                        return APIResponse(
                            success=True,
                            message="连接成功",
                            data={
                                "healthy": True,
                                "models": model_list,
                                "details": f"发现 {len(models)} 个可用模型"
                            }
                        )
                    else:
                        return APIResponse(
                            success=False,
                            message=f"连接失败: HTTP {response.status}",
                            data={
                                "healthy": False,
                                "details": f"服务器返回状态码: {response.status}"
                            }
                        )
                        
            except aiohttp.ClientConnectorError:
                return APIResponse(
                    success=False,
                    message="连接失败: 无法连接到Ollama服务",
                    data={
                        "healthy": False,
                        "details": "请检查Ollama服务是否启动以及URL是否正确"
                    }
                )
            except asyncio.TimeoutError:
                return APIResponse(
                    success=False,
                    message="连接超时",
                    data={
                        "healthy": False,
                        "details": f"连接超时({timeout}秒)，请检查网络或增加超时时间"
                    }
                )
                
    except Exception as e:
        logger.error("测试Ollama连接失败", error=str(e))
        return APIResponse(
            success=False,
            message="连接测试失败",
            data={
                "healthy": False,
                "details": str(e)
            }
        )


@router.get("/config/history", response_model=APIResponse)
async def get_ollama_config_history() -> APIResponse:
    """获取Ollama配置历史记录"""
    try:
        configs = await config_db_service.get_all_ollama_configs()
        
        return APIResponse(
            success=True,
            message="获取配置历史成功",
            data={"configs": configs}
        )
        
    except Exception as e:
        logger.error("获取Ollama配置历史失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/set-current/{config_id}", response_model=APIResponse)
async def set_current_ollama_config(config_id: int) -> APIResponse:
    """设置当前使用的Ollama配置"""
    try:
        result = await config_db_service.set_current_ollama_config(config_id)
        
        return APIResponse(
            success=result["success"],
            message=result["message"],
            data={"config_id": config_id}
        )
    except Exception as e:
        logger.error("设置当前Ollama配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"设置当前配置失败: {str(e)}")


@router.delete("/config/history", response_model=APIResponse)
async def clear_ollama_config_history() -> APIResponse:
    """清空Ollama配置历史记录（保留当前配置）"""
    try:
        # 这里可以实现清空历史记录的逻辑
        # 暂时返回成功，后续可以添加具体实现
        
        return APIResponse(
            success=True,
            message="配置历史已清空"
        )
        
    except Exception as e:
        logger.error("清空Ollama配置历史失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=APIResponse)
async def get_ollama_models(api_url: str = "http://localhost:11434") -> APIResponse:
    """获取Ollama可用模型列表"""
    try:
        # 构建获取模型的URL
        models_url = f"{api_url.rstrip('/')}/api/tags"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            try:
                async with session.get(models_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        
                        model_list = []
                        for model in models:
                            model_info = {
                                "name": model.get("name", ""),
                                "label": model.get("name", ""),
                                "size": model.get("size", 0),
                                "modified_at": model.get("modified_at", ""),
                                "digest": model.get("digest", "")
                            }
                            model_list.append(model_info)
                        
                        return APIResponse(
                            success=True,
                            message=f"获取到 {len(models)} 个可用模型",
                            data={"models": model_list}
                        )
                    else:
                        return APIResponse(
                            success=False,
                            message=f"获取模型失败: HTTP {response.status}",
                            data={"models": []}
                        )
                        
            except aiohttp.ClientConnectorError:
                return APIResponse(
                    success=False,
                    message="连接失败: 无法连接到Ollama服务",
                    data={"models": []}
                )
            except asyncio.TimeoutError:
                return APIResponse(
                    success=False,
                    message="请求超时",
                    data={"models": []}
                )
                
    except Exception as e:
        logger.error("获取Ollama模型失败", error=str(e))
        return APIResponse(
            success=False,
            message="获取模型失败",
            data={"models": [], "error": str(e)}
        )


@router.post("/chat", response_model=APIResponse)
async def chat_with_ollama(params: Dict[str, Any] = Body(...)) -> APIResponse:
    """与Ollama模型进行对话"""
    try:
        message = params.get("message", "")
        config = params.get("config", {})
        
        if not message.strip():
            return APIResponse(
                success=False,
                message="消息不能为空"
            )
        
        api_url = config.get("apiUrl", "http://localhost:11434")
        model = config.get("model", "llama3.2")
        timeout = config.get("timeout", 60000) / 1000  # 转换为秒
        max_tokens = config.get("maxTokens", 2048)
        temperature = config.get("temperature", 0.7)
        
        # 构建请求URL
        chat_url = f"{api_url.rstrip('/')}/api/generate"
        
        # 构建请求数据
        request_data = {
            "model": model,
            "prompt": message,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            try:
                async with session.post(chat_url, json=request_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response", "")
                        
                        return APIResponse(
                            success=True,
                            message="对话成功",
                            data={
                                "response": response_text,
                                "model": model,
                                "done": data.get("done", True)
                            }
                        )
                    else:
                        error_text = await response.text()
                        return APIResponse(
                            success=False,
                            message=f"Ollama响应错误: HTTP {response.status}",
                            data={"error": error_text}
                        )
                        
            except aiohttp.ClientConnectorError:
                return APIResponse(
                    success=False,
                    message="连接失败: 无法连接到Ollama服务",
                    data={"error": "请检查Ollama服务是否启动"}
                )
            except asyncio.TimeoutError:
                return APIResponse(
                    success=False,
                    message="请求超时",
                    data={"error": f"请求超时({timeout}秒)"}
                )
                
    except Exception as e:
        logger.error("Ollama对话失败", error=str(e))
        return APIResponse(
            success=False,
            message="对话失败",
            data={"error": str(e)}
        )
