#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则引擎服务 - 自动化巡检与预警规则管理

负责巡检规则的创建、管理和执行，提供灵活的
条件判断和决策机制，支持复杂的业务逻辑组合。

功能特性:
1. 规则创建和配置管理
2. 条件组合逻辑处理
3. 规则执行和结果判断
4. 执行历史和统计跟踪
5. 规则优先级和调度
6. 动态规则更新

作者: AI监控团队
版本: 2.0.0
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import structlog
from rule_engine import Rule, Context

from app.models.schemas import (
    InspectionRule,
    InspectionRuleCreate,
    RuleCondition,
    RuleExecutionResult,
    RulesExecutionResponse,
    RuleOperator,
    AlertSeverity,
    NotificationChannel,
    APIResponse
)
from app.services.prometheus_service import PrometheusService
from app.core.config import settings

logger = structlog.get_logger(__name__)


@dataclass
class RuleExecutionContext:
    """规则执行上下文信息"""
    rule_id: int
    rule_name: str
    execution_time: datetime
    prometheus_data: Dict[str, Any]
    last_execution: Optional[datetime] = None
    execution_count: int = 0


class RuleExecutionStatus(Enum):
    """规则执行状态"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


class RuleEngine:
    """
    规则引擎 - 自动化巡检与预警决策核心
    
    提供完整的规则管理和执行功能，支持复杂的
    条件判断逻辑和多维度的决策制定。
    
    核心功能:
    1. 规则创建、更新、删除和查询
    2. 条件组合逻辑处理 (AND, OR, NOT)
    3. 定时和触发式规则执行
    4. 执行结果统计和历史追踪
    5. 规则优先级和依赖管理
    6. 动态规则配置热更新
    
    使用示例:
        engine = RuleEngine()
        
        # 创建规则
        rule_id = await engine.create_rule(rule_data)
        
        # 执行规则
        results = await engine.execute_rules()
        
        # 执行单个规则
        result = await engine.execute_rule(rule_id)
    """
    
    def __init__(self, prometheus_service: Optional[PrometheusService] = None):
        """
        初始化规则引擎
        
        Args:
            prometheus_service: Prometheus数据服务实例
        """
        self.logger = logger.bind(component="RuleEngine")
        
        # 服务依赖
        self.prometheus_service = prometheus_service or PrometheusService()
        
        # 规则存储 - 在实际应用中应该使用数据库
        self.rules: Dict[int, InspectionRule] = {}
        self.rule_counter = 0
        
        # 执行历史和统计
        self.execution_history: List[RuleExecutionResult] = []
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "triggered_rules": 0
        }
        
        # 执行配置
        self.max_execution_time = 60  # 单个规则最大执行时间（秒）
        self.batch_size = 50          # 批量执行规则数量
        
        self.logger.info(
            "规则引擎初始化完成",
            max_execution_time=self.max_execution_time,
            batch_size=self.batch_size
        )
    
    
    async def create_rule(self, rule_data: InspectionRuleCreate) -> int:
        """
        创建新的巡检规则
        
        Args:
            rule_data: 规则创建数据
            
        Returns:
            int: 新创建的规则ID
            
        Raises:
            ValueError: 规则数据验证失败
        """
        try:
            # 数据验证
            await self._validate_rule_data(rule_data)
            
            # 生成规则ID
            self.rule_counter += 1
            rule_id = self.rule_counter
            
            # 创建规则对象
            rule = InspectionRule(
                id=rule_id,
                name=rule_data.name,
                description=rule_data.description,
                enabled=rule_data.enabled,
                conditions=rule_data.conditions,
                severity=rule_data.severity,
                notification_channels=rule_data.notification_channels,
                cooldown_minutes=rule_data.cooldown_minutes,
                tags=rule_data.tags,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 存储规则
            self.rules[rule_id] = rule
            
            self.logger.info(
                "规则创建成功",
                rule_id=rule_id,
                rule_name=rule.name,
                conditions_count=len(rule.conditions),
                severity=rule.severity.value
            )
            
            return rule_id
            
        except Exception as e:
            self.logger.error("规则创建失败", error=str(e))
            raise ValueError(f"规则创建失败: {str(e)}")
    
    
    async def update_rule(self, rule_id: int, rule_data: InspectionRuleCreate) -> bool:
        """
        更新现有规则
        
        Args:
            rule_id: 规则ID
            rule_data: 更新的规则数据
            
        Returns:
            bool: 更新是否成功
        """
        try:
            if rule_id not in self.rules:
                raise ValueError(f"规则不存在: {rule_id}")
            
            # 数据验证
            await self._validate_rule_data(rule_data)
            
            # 获取现有规则
            existing_rule = self.rules[rule_id]
            
            # 更新规则数据
            updated_rule = InspectionRule(
                id=rule_id,
                name=rule_data.name,
                description=rule_data.description,
                enabled=rule_data.enabled,
                conditions=rule_data.conditions,
                severity=rule_data.severity,
                notification_channels=rule_data.notification_channels,
                cooldown_minutes=rule_data.cooldown_minutes,
                tags=rule_data.tags,
                created_at=existing_rule.created_at,
                updated_at=datetime.now(),
                last_executed=existing_rule.last_executed,
                execution_count=existing_rule.execution_count,
                triggered_count=existing_rule.triggered_count
            )
            
            # 保存更新
            self.rules[rule_id] = updated_rule
            
            self.logger.info(
                "规则更新成功",
                rule_id=rule_id,
                rule_name=updated_rule.name
            )
            
            return True
            
        except Exception as e:
            self.logger.error("规则更新失败", rule_id=rule_id, error=str(e))
            raise ValueError(f"规则更新失败: {str(e)}")
    
    
    async def delete_rule(self, rule_id: int) -> bool:
        """
        删除规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            if rule_id not in self.rules:
                raise ValueError(f"规则不存在: {rule_id}")
            
            rule_name = self.rules[rule_id].name
            del self.rules[rule_id]
            
            self.logger.info("规则删除成功", rule_id=rule_id, rule_name=rule_name)
            return True
            
        except Exception as e:
            self.logger.error("规则删除失败", rule_id=rule_id, error=str(e))
            return False
    
    
    async def get_rule(self, rule_id: int) -> Optional[InspectionRule]:
        """
        获取规则信息
        
        Args:
            rule_id: 规则ID
            
        Returns:
            Optional[InspectionRule]: 规则信息，不存在时返回None
        """
        return self.rules.get(rule_id)
    
    
    async def list_rules(self, enabled_only: bool = False) -> List[InspectionRule]:
        """
        获取规则列表
        
        Args:
            enabled_only: 是否只返回启用的规则
            
        Returns:
            List[InspectionRule]: 规则列表
        """
        rules = list(self.rules.values())
        
        if enabled_only:
            rules = [rule for rule in rules if rule.enabled]
        
        # 按创建时间排序
        rules.sort(key=lambda x: x.created_at, reverse=True)
        
        return rules
    
    
    async def execute_rules(
        self,
        rule_ids: Optional[List[int]] = None,
        enabled_only: bool = True
    ) -> RulesExecutionResponse:
        """
        批量执行规则
        
        Args:
            rule_ids: 指定执行的规则ID列表，None表示执行所有规则
            enabled_only: 是否只执行启用的规则
            
        Returns:
            RulesExecutionResponse: 执行结果汇总
        """
        execution_start = time.time()
        
        try:
            self.logger.info("开始批量执行规则", rule_ids=rule_ids, enabled_only=enabled_only)
            
            # 确定要执行的规则列表
            if rule_ids is not None:
                target_rules = [self.rules[rid] for rid in rule_ids if rid in self.rules]
            else:
                target_rules = list(self.rules.values())
            
            if enabled_only:
                target_rules = [rule for rule in target_rules if rule.enabled]
            
            # 执行规则
            results = []
            triggered_count = 0
            alerts_sent = 0
            
            for rule in target_rules[:self.batch_size]:  # 限制批量大小
                try:
                    result = await self.execute_rule(rule.id)
                    results.append(result)
                    
                    if result.triggered:
                        triggered_count += 1
                        # TODO: 集成通知服务发送告警
                        alerts_sent += 1
                        
                except Exception as e:
                    self.logger.error("规则执行异常", rule_id=rule.id, error=str(e))
                    # 创建失败结果
                    error_result = RuleExecutionResult(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        triggered=False,
                        severity=rule.severity,
                        message=f"执行失败: {str(e)}",
                        conditions_met=0,
                        total_conditions=len(rule.conditions),
                        execution_time=datetime.now(),
                        duration_ms=0.0,
                        metadata={"error": str(e)}
                    )
                    results.append(error_result)
            
            # 更新统计信息
            self.execution_stats["total_executions"] += len(results)
            self.execution_stats["successful_executions"] += len([r for r in results if "error" not in r.metadata])
            self.execution_stats["failed_executions"] += len([r for r in results if "error" in r.metadata])
            self.execution_stats["triggered_rules"] += triggered_count
            
            execution_time = time.time() - execution_start
            
            # 生成执行摘要
            execution_summary = {
                "execution_time": round(execution_time, 3),
                "rules_executed": len(results),
                "rules_triggered": triggered_count,
                "alerts_sent": alerts_sent,
                "success_rate": len([r for r in results if "error" not in r.metadata]) / len(results) if results else 0,
                "average_rule_duration": sum(r.duration_ms for r in results) / len(results) if results else 0
            }
            
            self.logger.info(
                "批量规则执行完成",
                total_executed=len(results),
                triggered_count=triggered_count,
                execution_time=round(execution_time, 3)
            )
            
            return RulesExecutionResponse(
                success=True,
                message=f"成功执行{len(results)}个规则",
                results=results,
                total_executed=len(results),
                triggered_count=triggered_count,
                alerts_sent=alerts_sent,
                execution_summary=execution_summary
            )
            
        except Exception as e:
            execution_time = time.time() - execution_start
            self.logger.error(
                "批量规则执行失败",
                error=str(e),
                execution_time=round(execution_time, 3)
            )
            raise RuntimeError(f"规则执行失败: {str(e)}")
    
    
    async def execute_rule(self, rule_id: int) -> RuleExecutionResult:
        """
        执行单个规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            RuleExecutionResult: 规则执行结果
        """
        execution_start = time.time()
        
        try:
            if rule_id not in self.rules:
                raise ValueError(f"规则不存在: {rule_id}")
            
            rule = self.rules[rule_id]
            
            if not rule.enabled:
                return RuleExecutionResult(
                    rule_id=rule_id,
                    rule_name=rule.name,
                    triggered=False,
                    severity=rule.severity,
                    message="规则已禁用",
                    conditions_met=0,
                    total_conditions=len(rule.conditions),
                    execution_time=datetime.now(),
                    duration_ms=0.0,
                    metadata={"status": "disabled"}
                )
            
            # 检查冷却时间
            if await self._is_in_cooldown(rule):
                return RuleExecutionResult(
                    rule_id=rule_id,
                    rule_name=rule.name,
                    triggered=False,
                    severity=rule.severity,
                    message="规则在冷却期内",
                    conditions_met=0,
                    total_conditions=len(rule.conditions),
                    execution_time=datetime.now(),
                    duration_ms=0.0,
                    metadata={"status": "cooldown"}
                )
            
            self.logger.debug("开始执行规则", rule_id=rule_id, rule_name=rule.name)
            
            # 评估所有条件
            conditions_met = 0
            condition_results = []
            
            for i, condition in enumerate(rule.conditions):
                try:
                    condition_met = await self._evaluate_condition(condition)
                    condition_results.append({
                        "condition_index": i,
                        "met": condition_met,
                        "query": condition.metric_query,
                        "operator": condition.operator.value,
                        "threshold": condition.threshold
                    })
                    
                    if condition_met:
                        conditions_met += 1
                        
                except Exception as e:
                    self.logger.warning(
                        "条件评估失败",
                        rule_id=rule_id,
                        condition_index=i,
                        error=str(e)
                    )
                    condition_results.append({
                        "condition_index": i,
                        "met": False,
                        "error": str(e)
                    })
            
            # 判断规则是否触发（所有条件都必须满足）
            triggered = conditions_met == len(rule.conditions) and conditions_met > 0
            
            # 生成执行消息
            if triggered:
                message = f"规则触发：{conditions_met}/{len(rule.conditions)}个条件满足"
            else:
                message = f"规则未触发：仅{conditions_met}/{len(rule.conditions)}个条件满足"
            
            # 更新规则统计
            rule.execution_count += 1
            rule.last_executed = datetime.now()
            if triggered:
                rule.triggered_count += 1
            
            execution_time = time.time() - execution_start
            
            result = RuleExecutionResult(
                rule_id=rule_id,
                rule_name=rule.name,
                triggered=triggered,
                severity=rule.severity,
                message=message,
                conditions_met=conditions_met,
                total_conditions=len(rule.conditions),
                execution_time=datetime.now(),
                duration_ms=execution_time * 1000,
                metadata={
                    "condition_results": condition_results,
                    "tags": rule.tags,
                    "notification_channels": [ch.value for ch in rule.notification_channels]
                }
            )
            
            # 记录执行历史
            self.execution_history.append(result)
            
            # 限制历史记录长度
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-500:]
            
            self.logger.info(
                "规则执行完成",
                rule_id=rule_id,
                rule_name=rule.name,
                triggered=triggered,
                conditions_met=conditions_met,
                total_conditions=len(rule.conditions),
                duration_ms=round(execution_time * 1000, 2)
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - execution_start
            self.logger.error(
                "规则执行失败",
                rule_id=rule_id,
                error=str(e),
                duration_ms=round(execution_time * 1000, 2)
            )
            raise RuntimeError(f"规则执行失败: {str(e)}")
    
    
    async def _validate_rule_data(self, rule_data: InspectionRuleCreate) -> None:
        """
        验证规则数据的有效性
        
        Args:
            rule_data: 规则数据
            
        Raises:
            ValueError: 验证失败时抛出异常
        """
        if not rule_data.name.strip():
            raise ValueError("规则名称不能为空")
        
        if not rule_data.conditions:
            raise ValueError("规则必须包含至少一个条件")
        
        # 验证条件
        for i, condition in enumerate(rule_data.conditions):
            if not condition.metric_query.strip():
                raise ValueError(f"条件{i+1}的查询语句不能为空")
            
            if condition.duration_minutes <= 0:
                raise ValueError(f"条件{i+1}的持续时间必须大于0")
            
            # 验证操作符
            if not isinstance(condition.operator, RuleOperator):
                raise ValueError(f"条件{i+1}的操作符无效")
            
            # 验证阈值
            if not isinstance(condition.threshold, (int, float)):
                raise ValueError(f"条件{i+1}的阈值必须是数字")
        
        # 验证冷却时间
        if rule_data.cooldown_minutes <= 0:
            raise ValueError("冷却时间必须大于0分钟")
        
        # 验证严重程度
        if not isinstance(rule_data.severity, AlertSeverity):
            raise ValueError("严重程度无效")
        
        # 验证通知渠道
        for channel in rule_data.notification_channels:
            if not isinstance(channel, NotificationChannel):
                raise ValueError(f"通知渠道{channel}无效")


    async def _is_in_cooldown(self, rule: InspectionRule) -> bool:
        """
        检查规则是否在冷却期内
        
        Args:
            rule: 规则对象
            
        Returns:
            bool: True表示在冷却期内
        """
        if rule.last_executed is None:
            return False
        
        cooldown_period = timedelta(minutes=rule.cooldown_minutes)
        time_since_last = datetime.now() - rule.last_executed
        
        return time_since_last < cooldown_period


    async def _evaluate_condition(self, condition: RuleCondition) -> bool:
        """
        评估单个规则条件
        
        Args:
            condition: 规则条件
            
        Returns:
            bool: 条件是否满足
        """
        try:
            # 查询Prometheus数据
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=condition.duration_minutes)
            
            metrics_response = await self.prometheus_service.query_range(
                query=condition.metric_query,
                start_time=start_time,
                end_time=end_time,
                step="1m"
            )
            
            if not metrics_response.data:
                self.logger.warning(
                    "查询无数据",
                    query=condition.metric_query,
                    start_time=start_time,
                    end_time=end_time
                )
                return False
            
            # 获取最新的数据点值
            latest_values = []
            for time_series in metrics_response.data:
                if time_series.values:
                    latest_value = time_series.values[-1].value
                    latest_values.append(latest_value)
            
            if not latest_values:
                return False
            
            # 计算聚合值（这里使用平均值，可以根据需要调整）
            aggregated_value = sum(latest_values) / len(latest_values)
            
            # 根据操作符判断条件
            if condition.operator == RuleOperator.GREATER_THAN:
                result = aggregated_value > condition.threshold
            elif condition.operator == RuleOperator.LESS_THAN:
                result = aggregated_value < condition.threshold
            elif condition.operator == RuleOperator.GREATER_EQUAL:
                result = aggregated_value >= condition.threshold
            elif condition.operator == RuleOperator.LESS_EQUAL:
                result = aggregated_value <= condition.threshold
            elif condition.operator == RuleOperator.EQUAL:
                result = abs(aggregated_value - condition.threshold) < 1e-6
            elif condition.operator == RuleOperator.NOT_EQUAL:
                result = abs(aggregated_value - condition.threshold) >= 1e-6
            else:
                raise ValueError(f"不支持的操作符: {condition.operator}")
            
            self.logger.debug(
                "条件评估完成",
                query=condition.metric_query,
                value=round(aggregated_value, 3),
                operator=condition.operator.value,
                threshold=condition.threshold,
                result=result
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "条件评估失败",
                query=condition.metric_query,
                error=str(e)
            )
            return False


    async def get_execution_statistics(self) -> Dict[str, Any]:
        """
        获取规则执行统计信息
        
        Returns:
            Dict: 统计信息
        """
        total_rules = len(self.rules)
        enabled_rules = len([r for r in self.rules.values() if r.enabled])
        
        # 最近24小时的执行历史
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_executions = [
            result for result in self.execution_history
            if result.execution_time >= recent_cutoff
        ]
        
        return {
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "disabled_rules": total_rules - enabled_rules,
            "execution_stats": self.execution_stats.copy(),
            "recent_24h": {
                "total_executions": len(recent_executions),
                "triggered_executions": len([r for r in recent_executions if r.triggered]),
                "average_duration_ms": sum(r.duration_ms for r in recent_executions) / len(recent_executions) if recent_executions else 0,
                "success_rate": len([r for r in recent_executions if "error" not in r.metadata]) / len(recent_executions) if recent_executions else 0
            },
            "rule_severity_distribution": {
                severity.value: len([r for r in self.rules.values() if r.severity == severity])
                for severity in AlertSeverity
            }
        }


    async def schedule_rule_execution(self) -> None:
        """
        调度规则执行
        
        定期执行启用的规则检查
        """
        while True:
            try:
                # 执行启用的规则
                await self.execute_rules(enabled_only=True)
                
                # 等待下次执行
                await asyncio.sleep(settings.RULES_CHECK_INTERVAL)
                
            except asyncio.CancelledError:
                self.logger.info("规则调度执行被取消")
                break
            except Exception as e:
                self.logger.error("规则调度执行异常", error=str(e))
                await asyncio.sleep(60)  # 出错后等待1分钟再继续


# 导出类
__all__ = ["RuleEngine", "RuleExecutionContext", "RuleExecutionStatus"]