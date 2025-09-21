#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prometheus配置管理API端点

提供Prometheus数据源配置管理功能，包括：
1. 获取Prometheus配置
2. 更新Prometheus配置
3. 测试Prometheus连接

作者: AI监控团队
版本: 2.0.0
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import Response
import structlog
import aiohttp
import asyncio

from app.models.schemas import APIResponse
from app.core.config import settings
from app.services.prometheus_service import PrometheusService
from app.services.config_service import config_service
from app.services.config_db_service import config_db_service

logger = structlog.get_logger(__name__)

# 创建路由器
router = APIRouter()


@router.post("/config/validate-name", response_model=APIResponse)
async def validate_config_name(request_data: Dict[str, str] = Body(...)) -> APIResponse:
    """验证配置名称"""
    try:
        name = request_data.get("name", "")
        validation_result = config_db_service.validate_config_name(name)
        
        return APIResponse(
            success=validation_result["valid"],
            message=validation_result.get("message", "配置名称验证通过"),
            data=validation_result
        )
    except Exception as e:
        logger.error("配置名称验证失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"配置名称验证失败: {str(e)}")


@router.post("/config/set-current/{config_id}", response_model=APIResponse)
async def set_current_config(config_id: int) -> APIResponse:
    """设置当前使用的Prometheus配置"""
    try:
        result = await config_db_service.set_current_prometheus_config(config_id)
        
        return APIResponse(
            success=result["success"],
            message=result["message"],
            data={"config_id": config_id}
        )
    except Exception as e:
        logger.error("设置当前配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"设置当前配置失败: {str(e)}")


@router.get("/config", response_model=APIResponse)
async def get_prometheus_config() -> APIResponse:
    """获取Prometheus配置"""
    try:
        # 优先从数据库获取配置
        db_config = await config_db_service.get_default_prometheus_config()
        if db_config:
            config = {
                "name": db_config["name"],  # 添加配置名称字段
                "enabled": db_config["is_enabled"],
                "url": db_config["url"],
                "username": db_config["username"],
                "password": db_config["password"],
                "timeout": db_config["timeout"],
                "scrapeInterval": db_config["scrape_interval"],
                "evaluationInterval": db_config["evaluation_interval"],
                "max_retries": db_config["max_retries"],
                "targets": []
            }
        else:
            # 从配置文件获取默认配置
            config = config_service.get_prometheus_config()
            # 确保配置文件的配置也有name字段
            if "name" not in config:
                config["name"] = "默认配置"
        
        return APIResponse(
            success=True,
            message="获取Prometheus配置成功",
            data={"config": config}
        )
        
    except Exception as e:
        logger.error("获取Prometheus配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config", response_model=APIResponse)
async def update_prometheus_config(config: Dict[str, Any] = Body(..., description="Prometheus配置")) -> APIResponse:
    """更新Prometheus配置"""
    try:
        # 保存配置到数据库
        result = await config_db_service.save_prometheus_config(config)
        
        # 检查保存结果
        if not result.get("success", True):
            return APIResponse(
                success=False,
                message=result.get("message", "配置保存失败"),
                data=result
            )
        
        # 同时保存到配置文件作为备份
        try:
            config_service.update_prometheus_config(config)
        except Exception as e:
            logger.warning("保存到配置文件失败", error=str(e))
        
        return APIResponse(
            success=True,
            message=result.get("message", "Prometheus配置更新成功"),
            data=result
        )
        
    except Exception as e:
        logger.error("更新Prometheus配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.options("/test")
async def test_prometheus_connection_options(request: Request) -> Response:
    """处理OPTIONS预检请求"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400"
        }
    )


@router.post("/test", response_model=APIResponse)
async def test_prometheus_connection(config: Dict[str, Any] = Body(..., description="Prometheus配置")) -> APIResponse:
    """测试Prometheus连接"""
    try:
        # 创建临时Prometheus服务实例用于测试
        prometheus_service = PrometheusService()
        
        # 如果提供了URL，则使用提供的URL
        if "url" in config and config["url"]:
            prometheus_service.base_url = config["url"].rstrip('/')
        
        # 执行健康检查
        is_healthy = await prometheus_service.health_check()
        
        if is_healthy:
            return APIResponse(
                success=True,
                message="Prometheus连接测试成功",
                data={"healthy": True}
            )
        else:
            return APIResponse(
                success=False,
                message="Prometheus连接测试失败，请检查配置",
                data={"healthy": False}
            )
            
    except Exception as e:
        logger.error("Prometheus连接测试失败", error=str(e))
        return APIResponse(
            success=False,
            message=f"Prometheus连接测试失败: {str(e)}",
            data={"healthy": False, "error": str(e)}
        )


# 配置历史管理端点
@router.get("/config/history", response_model=APIResponse)
async def get_prometheus_config_history() -> APIResponse:
    """获取Prometheus配置历史记录"""
    try:
        from app.services.config_db_service import config_db_service
        
        configs = await config_db_service.get_all_prometheus_configs()
        
        return APIResponse(
            success=True,
            message="获取配置历史成功",
            data={"configs": configs}
        )
        
    except Exception as e:
        logger.error("获取配置历史失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/restore/{config_id}", response_model=APIResponse)
async def restore_prometheus_config(config_id: int) -> APIResponse:
    """恢复指定的Prometheus配置"""
    try:
        from app.services.config_db_service import config_db_service
        
        # 获取指定配置
        config = await config_db_service.get_prometheus_config_by_id(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        # 设置为当前配置
        await config_db_service.set_current_prometheus_config(config_id)
        
        return APIResponse(
            success=True,
            message="配置恢复成功",
            data={"config": config}
        )
        
    except Exception as e:
        logger.error("恢复配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/create", response_model=APIResponse)
async def create_prometheus_config(config: Dict[str, Any] = Body(...)) -> APIResponse:
    """创建新的Prometheus配置"""
    try:
        from app.services.config_db_service import config_db_service
        
        # 保存新配置
        saved_config = await config_db_service.save_prometheus_config(config)
        
        return APIResponse(
            success=True,
            message="配置创建成功",
            data={"config": saved_config}
        )
        
    except Exception as e:
        logger.error("创建配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/config/{config_id}", response_model=APIResponse)
async def delete_prometheus_config(config_id: int) -> APIResponse:
    """删除指定的Prometheus配置"""
    try:
        from app.services.config_db_service import config_db_service
        
        # 检查是否为当前使用的配置
        config = await config_db_service.get_prometheus_config_by_id(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        if config.get('is_current', False):
            raise HTTPException(status_code=400, detail="无法删除当前使用的配置")
        
        # 删除配置
        await config_db_service.delete_prometheus_config(config_id)
        
        return APIResponse(
            success=True,
            message="配置删除成功"
        )
        
    except Exception as e:
        logger.error("删除配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/config/history", response_model=APIResponse)
async def clear_prometheus_config_history() -> APIResponse:
    """清空配置历史记录（保留当前配置）"""
    try:
        from app.services.config_db_service import config_db_service
        
        await config_db_service.clear_config_history()
        
        return APIResponse(
            success=True,
            message="配置历史已清空"
        )
        
    except Exception as e:
        logger.error("清空配置历史失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# PromQL查询端点
@router.post("/query", response_model=APIResponse)
async def execute_promql_query(query_params: Dict[str, Any] = Body(...)) -> APIResponse:
    """执行PromQL查询"""
    try:
        
        # 获取当前Prometheus配置
        config = await config_db_service.get_default_prometheus_config()
        if not config:
            # 使用默认配置
            config = {
                "url": "http://192.168.233.137:30090",
                "timeout": 30,
                "username": None,
                "password": None
            }
        
        prometheus_url = config['url'].rstrip('/')
        query = query_params.get('query')
        query_type = query_params.get('queryType', 'query')
        
        if not query:
            raise HTTPException(status_code=400, detail="查询语句不能为空")
        
        # 构建查询URL
        if query_type == 'query':
            # 即时查询
            url = f"{prometheus_url}/api/v1/query"
            params = {'query': query}
            if query_params.get('time'):
                params['time'] = query_params['time']
        else:
            # 范围查询
            url = f"{prometheus_url}/api/v1/query_range"
            params = {
                'query': query,
                'start': query_params.get('start'),
                'end': query_params.get('end'),
                'step': query_params.get('step', '15s')
            }
        
        # 发送查询请求
        timeout = aiohttp.ClientTimeout(total=30)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return APIResponse(
                            success=True,
                            message="查询执行成功",
                            data=result
                        )
                    else:
                        error_text = await response.text()
                        logger.error("Prometheus查询失败", status=response.status, error=error_text)
                        raise HTTPException(status_code=response.status, detail=f"Prometheus查询失败: {error_text}")
        except aiohttp.ClientError as e:
            logger.error("连接Prometheus失败", error=str(e))
            raise HTTPException(status_code=503, detail=f"无法连接到Prometheus服务器: {str(e)}")
        except asyncio.TimeoutError:
            logger.error("Prometheus查询超时")
            raise HTTPException(status_code=504, detail="Prometheus查询超时")
        
    except Exception as e:
        logger.error("PromQL查询失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=APIResponse)
async def get_prometheus_metrics() -> APIResponse:
    """获取Prometheus指标列表"""
    try:
        
        # 获取当前Prometheus配置
        config = await config_db_service.get_default_prometheus_config()
        if not config:
            raise HTTPException(status_code=404, detail="未找到Prometheus配置")
        
        prometheus_url = config['url'].rstrip('/')
        url = f"{prometheus_url}/api/v1/label/__name__/values"
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return APIResponse(
                        success=True,
                        message="获取指标列表成功",
                        data=result
                    )
                else:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_text)
        
    except Exception as e:
        logger.error("获取指标列表失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/targets", response_model=APIResponse)
async def get_prometheus_targets() -> APIResponse:
    """获取Prometheus监控目标"""
    try:
        
        # 获取当前Prometheus配置
        config = await config_db_service.get_default_prometheus_config()
        if not config:
            raise HTTPException(status_code=404, detail="未找到Prometheus配置")
        
        prometheus_url = config['url'].rstrip('/')
        url = f"{prometheus_url}/api/v1/targets"
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return APIResponse(
                        success=True,
                        message="获取监控目标成功",
                        data=result
                    )
                else:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=error_text)
        
    except Exception as e:
        logger.error("获取监控目标失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))