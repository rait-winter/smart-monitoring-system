#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则管理API端点 - 巡检规则CRUD接口

提供巡检规则的创建、查询、更新、删除和执行功能。
支持规则条件配置、执行调度和结果统计。

端点功能:
1. POST /rules - 创建规则
2. GET /rules - 查询规则列表
3. GET /rules/{rule_id} - 获取规则详情
4. PUT /rules/{rule_id} - 更新规则
5. DELETE /rules/{rule_id} - 删除规则
6. POST /rules/execute - 执行规则
7. GET /rules/statistics - 规则统计

作者: AI监控团队
版本: 2.0.0
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Path
import structlog

from app.models.schemas import (
    InspectionRuleCreate,
    InspectionRule,
    RulesExecutionResponse,
    APIResponse
)
from app.services.rule_engine import RuleEngine
from app.services.prometheus_service import PrometheusService

logger = structlog.get_logger(__name__)

# 创建路由器
router = APIRouter()

# 服务实例
rule_engine = RuleEngine()


@router.post("/", response_model=APIResponse)
async def create_rule(rule_data: InspectionRuleCreate) -> APIResponse:
    """创建新的巡检规则"""
    try:
        rule_id = await rule_engine.create_rule(rule_data)
        
        return APIResponse(
            success=True,
            message="规则创建成功",
            data={"rule_id": rule_id, "rule_name": rule_data.name}
        )
    except Exception as e:
        logger.error("创建规则失败", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=APIResponse)
async def list_rules(
    enabled_only: bool = Query(False, description="是否只返回启用的规则")
) -> APIResponse:
    """获取规则列表"""
    try:
        rules = await rule_engine.list_rules(enabled_only=enabled_only)
        
        return APIResponse(
            success=True,
            message="获取规则列表成功",
            data={"rules": rules, "total": len(rules)}
        )
    except Exception as e:
        logger.error("获取规则列表失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{rule_id}", response_model=APIResponse)
async def get_rule(rule_id: int = Path(..., description="规则ID")) -> APIResponse:
    """获取规则详情"""
    try:
        rule = await rule_engine.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail=f"规则不存在: {rule_id}")
        
        return APIResponse(
            success=True,
            message="获取规则详情成功",
            data={"rule": rule}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取规则详情失败", rule_id=rule_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{rule_id}", response_model=APIResponse)
async def update_rule(
    rule_id: int = Path(..., description="规则ID"),
    rule_data: InspectionRuleCreate = None
) -> APIResponse:
    """更新规则"""
    try:
        success = await rule_engine.update_rule(rule_id, rule_data)
        if not success:
            raise HTTPException(status_code=404, detail=f"规则不存在: {rule_id}")
        
        return APIResponse(
            success=True,
            message="规则更新成功",
            data={"rule_id": rule_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("更新规则失败", rule_id=rule_id, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{rule_id}", response_model=APIResponse)
async def delete_rule(rule_id: int = Path(..., description="规则ID")) -> APIResponse:
    """删除规则"""
    try:
        success = await rule_engine.delete_rule(rule_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"规则不存在: {rule_id}")
        
        return APIResponse(
            success=True,
            message="规则删除成功",
            data={"rule_id": rule_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("删除规则失败", rule_id=rule_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=RulesExecutionResponse)
async def execute_rules(
    rule_ids: Optional[List[int]] = Query(None, description="指定执行的规则ID列表"),
    enabled_only: bool = Query(True, description="是否只执行启用的规则")
) -> RulesExecutionResponse:
    """执行规则检查"""
    try:
        results = await rule_engine.execute_rules(
            rule_ids=rule_ids,
            enabled_only=enabled_only
        )
        
        return results
    except Exception as e:
        logger.error("执行规则失败", rule_ids=rule_ids, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=APIResponse)
async def get_statistics() -> APIResponse:
    """获取规则执行统计"""
    try:
        stats = await rule_engine.get_execution_statistics()
        
        return APIResponse(
            success=True,
            message="获取统计信息成功",
            data=stats
        )
    except Exception as e:
        logger.error("获取统计信息失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))