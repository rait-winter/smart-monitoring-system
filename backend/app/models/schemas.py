#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic数据模型 - API请求/响应schema
支持高级数据验证、序列化和文档生成
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from pydantic import constr, conint, confloat
from typing import Annotated


# ===== 枚举类定义 =====

class AlertSeverity(str, Enum):
    """告警严重程度枚举"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"


class AlgorithmType(str, Enum):
    """AI异常检测算法类型"""
    ISOLATION_FOREST = "isolation_forest"
    Z_SCORE = "z_score"
    LSTM = "lstm"
    PROPHET = "prophet"
    STATISTICAL = "statistical"


class NotificationChannel(str, Enum):
    """通知渠道枚举"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"


class RuleOperator(str, Enum):
    """规则操作符枚举"""
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="


# ===== 基础模型 =====

class BaseSchema(BaseModel):
    """基础Schema配置"""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )


class TimestampMixin(BaseSchema):
    """时间戳混入类"""
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


# ===== 响应基类 =====

class APIResponse(BaseSchema):
    """标准API响应格式"""
    success: bool = Field(default=True, description="请求是否成功")
    message: str = Field(default="操作成功", description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    data: Optional[Dict[str, Any]] = Field(default=None, description="响应数据")


class PaginatedResponse(APIResponse):
    """分页响应格式"""
    total: int = Field(ge=0, description="总数量")
    page: int = Field(ge=1, description="当前页码")
    size: int = Field(ge=1, le=1000, description="每页大小")
    pages: int = Field(ge=0, description="总页数")


# ===== 健康检查 =====

class HealthCheckResponse(APIResponse):
    """系统健康检查响应"""
    service: str = Field(description="服务名称")
    version: str = Field(description="服务版本")
    environment: str = Field(description="运行环境")
    uptime: float = Field(ge=0, description="运行时间（秒）")
    components: Dict[str, str] = Field(default_factory=dict, description="组件状态")


# ===== 用户认证 =====

class UserLogin(BaseSchema):
    """用户登录请求"""
    username: Annotated[str, Field(min_length=3, max_length=50)] = Field(description="用户名")
    password: Annotated[str, Field(min_length=6, max_length=128)] = Field(description="密码")
    remember_me: bool = Field(default=False, description="记住登录状态")


class TokenResponse(APIResponse):
    """Token响应"""
    access_token: str = Field(description="访问令牌")
    refresh_token: str = Field(description="刷新令牌") 
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="过期时间（秒）")


class UserProfile(BaseSchema):
    """用户信息"""
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    email: str = Field(description="邮箱")
    full_name: Optional[str] = Field(default=None, description="全名")
    is_active: bool = Field(default=True, description="是否激活")
    role: str = Field(default="user", description="用户角色")


# ===== 指标数据 =====

class MetricDataPoint(BaseSchema):
    """指标数据点"""
    timestamp: datetime = Field(description="时间戳")
    value: float = Field(description="指标值")
    labels: Dict[str, str] = Field(default_factory=dict, description="标签")


class TimeSeriesData(BaseSchema):
    """时间序列数据"""
    metric_name: str = Field(description="指标名称")
    labels: Dict[str, str] = Field(default_factory=dict, description="指标标签")
    values: List[MetricDataPoint] = Field(description="数据点列表")


class MetricsQueryRequest(BaseSchema):
    """指标查询请求"""
    query: Annotated[str, Field(min_length=1, max_length=1000)] = Field(description="PromQL查询语句")
    start_time: datetime = Field(description="开始时间")
    end_time: datetime = Field(description="结束时间")
    step: str = Field(default="1m", description="查询步长")
    
    @field_validator('end_time')
    @classmethod
    def validate_time_range(cls, v, info):
        """验证时间范围"""
        if hasattr(info.data, 'start_time') and v <= info.data['start_time']:
            raise ValueError('结束时间必须大于开始时间')
        return v


class MetricsResponse(APIResponse):
    """指标数据响应"""
    data: List[TimeSeriesData] = Field(description="时间序列数据")
    query: str = Field(description="查询语句")
    execution_time: float = Field(description="查询耗时（秒）")


# ===== AI异常检测 =====

class AnomalyDetectionRequest(BaseSchema):
    """异常检测请求"""
    metric_query: Annotated[str, Field(min_length=1, max_length=1000)] = Field(description="指标查询")
    lookback_hours: Annotated[int, Field(ge=1, le=168)] = Field(default=24, description="回看小时数")
    algorithm: AlgorithmType = Field(default=AlgorithmType.ISOLATION_FOREST, description="检测算法")
    sensitivity: Annotated[float, Field(ge=0.1, le=1.0)] = Field(default=0.8, description="敏感度")
    threshold: Optional[float] = Field(default=None, description="自定义阈值")


class AnomalyPoint(BaseSchema):
    """异常点信息"""
    timestamp: datetime = Field(description="异常时间")
    value: float = Field(description="异常值")
    anomaly_score: Annotated[float, Field(ge=0.0, le=1.0)] = Field(description="异常分数")
    severity: AlertSeverity = Field(description="严重程度")
    explanation: Optional[str] = Field(default=None, description="异常说明")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加信息")


class AnomalyDetectionResult(BaseSchema):
    """异常检测结果"""
    model_config = ConfigDict(protected_namespaces=())
    
    anomalies: List[AnomalyPoint] = Field(description="异常点列表")
    total_points: int = Field(ge=0, description="总数据点数")
    anomaly_count: int = Field(ge=0, description="异常点数量")
    overall_score: Annotated[float, Field(ge=0.0, le=1.0)] = Field(description="整体异常分数")
    algorithm_used: AlgorithmType = Field(description="使用的算法")
    execution_time: float = Field(ge=0, description="执行耗时")
    recommendations: List[str] = Field(default_factory=list, description="建议操作")
    algorithm_info: Dict[str, Any] = Field(default_factory=dict, description="算法信息")


class AnomalyDetectionResponse(APIResponse):
    """异常检测响应"""
    result: AnomalyDetectionResult = Field(description="检测结果")
    request_params: AnomalyDetectionRequest = Field(description="请求参数")


# ===== 规则引擎 =====

class RuleCondition(BaseSchema):
    """规则条件"""
    metric_query: Annotated[str, Field(min_length=1, max_length=1000)] = Field(description="指标查询")
    operator: RuleOperator = Field(description="比较操作符")
    threshold: float = Field(description="阈值")
    duration_minutes: Annotated[int, Field(ge=1, le=1440)] = Field(default=5, description="持续时间（分钟）")


class InspectionRuleCreate(BaseSchema):
    """巡检规则创建请求"""
    name: Annotated[str, Field(min_length=1, max_length=200)] = Field(description="规则名称")
    description: Optional[Annotated[str, Field(max_length=500)]] = Field(default=None, description="规则描述")
    enabled: bool = Field(default=True, description="是否启用")
    conditions: List[RuleCondition] = Field(min_items=1, description="规则条件列表")
    severity: AlertSeverity = Field(default=AlertSeverity.MEDIUM, description="告警级别")
    notification_channels: List[NotificationChannel] = Field(
        default=[NotificationChannel.EMAIL], description="通知渠道"
    )
    cooldown_minutes: Annotated[int, Field(ge=1, le=1440)] = Field(default=15, description="冷却时间（分钟）")
    tags: List[str] = Field(default_factory=list, description="标签")


class InspectionRule(InspectionRuleCreate, TimestampMixin):
    """巡检规则（完整信息）"""
    id: int = Field(description="规则ID")
    last_executed: Optional[datetime] = Field(default=None, description="上次执行时间")
    execution_count: int = Field(default=0, description="执行次数")
    triggered_count: int = Field(default=0, description="触发次数")


class RuleExecutionResult(BaseSchema):
    """规则执行结果"""
    rule_id: int = Field(description="规则ID")
    rule_name: str = Field(description="规则名称")
    triggered: bool = Field(description="是否触发")
    severity: AlertSeverity = Field(description="告警级别")
    message: str = Field(description="执行结果消息")
    conditions_met: int = Field(ge=0, description="满足的条件数")
    total_conditions: int = Field(ge=1, description="总条件数")
    execution_time: datetime = Field(default_factory=datetime.utcnow, description="执行时间")
    duration_ms: float = Field(ge=0, description="执行耗时（毫秒）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加信息")


class RulesExecutionResponse(APIResponse):
    """规则执行响应"""
    results: List[RuleExecutionResult] = Field(description="执行结果列表")
    total_executed: int = Field(ge=0, description="总执行数")
    triggered_count: int = Field(ge=0, description="触发数量")
    alerts_sent: int = Field(ge=0, description="发送告警数")
    execution_summary: Dict[str, Any] = Field(description="执行摘要")


# ===== 通知系统 =====

class NotificationRequest(BaseSchema):
    """通知发送请求"""
    title: Annotated[str, Field(min_length=1, max_length=200)] = Field(description="通知标题")
    message: Annotated[str, Field(min_length=1, max_length=2000)] = Field(description="通知内容")
    severity: AlertSeverity = Field(description="严重程度")
    channels: List[NotificationChannel] = Field(description="通知渠道")
    recipients: Optional[List[str]] = Field(default=None, description="收件人列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加信息")


class NotificationStatus(BaseSchema):
    """通知状态"""
    notification_id: str = Field(description="通知ID")
    channel: NotificationChannel = Field(description="通知渠道")
    status: str = Field(description="发送状态") # pending, sent, failed
    sent_at: Optional[datetime] = Field(default=None, description="发送时间")
    error_message: Optional[str] = Field(default=None, description="错误信息")


class NotificationResponse(APIResponse):
    """通知发送响应"""
    notification_id: str = Field(description="通知ID")
    statuses: Dict[str, NotificationStatus] = Field(description="各渠道发送状态")


# ===== 系统统计 =====

class SystemStats(BaseSchema):
    """系统统计信息"""
    total_metrics: int = Field(ge=0, description="监控指标总数")
    active_rules: int = Field(ge=0, description="激活规则数")
    alerts_last_24h: int = Field(ge=0, description="最近24小时告警数")
    anomalies_detected: int = Field(ge=0, description="检测到的异常数")
    system_uptime: str = Field(description="系统运行时间")
    last_inspection: Optional[datetime] = Field(default=None, description="最后巡检时间")
    prometheus_targets: Dict[str, int] = Field(default_factory=dict, description="Prometheus目标状态")


class DashboardData(BaseSchema):
    """仪表盘数据"""
    stats: SystemStats = Field(description="系统统计")
    recent_alerts: List[Dict[str, Any]] = Field(default_factory=list, description="最近告警")
    top_metrics: List[Dict[str, Any]] = Field(default_factory=list, description="重要指标")
    system_health: Dict[str, Any] = Field(default_factory=dict, description="系统健康状态")


# ===== 导出所有模型 =====
__all__ = [
    # 枚举
    "AlertSeverity", "AlgorithmType", "NotificationChannel", "RuleOperator",
    # 基础类
    "BaseSchema", "TimestampMixin", "APIResponse", "PaginatedResponse",
    # 健康检查
    "HealthCheckResponse",
    # 用户认证
    "UserLogin", "TokenResponse", "UserProfile",
    # 指标数据
    "MetricDataPoint", "TimeSeriesData", "MetricsQueryRequest", "MetricsResponse",
    # AI异常检测
    "AnomalyDetectionRequest", "AnomalyPoint", "AnomalyDetectionResult", "AnomalyDetectionResponse",
    # 规则引擎
    "RuleCondition", "InspectionRuleCreate", "InspectionRule", "RuleExecutionResult", "RulesExecutionResponse",
    # 通知系统
    "NotificationRequest", "NotificationStatus", "NotificationResponse",
    # 系统统计
    "SystemStats", "DashboardData",
]