#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型定义 - 智能监控预警系统

定义所有数据表的ORM模型，包括用户、规则、告警、通知等核心实体。

模型列表:
1. User - 系统用户
2. InspectionRule - 巡检规则
3. Alert - 告警记录
4. Notification - 通知记录
5. Anomaly - 异常记录
6. SystemLog - 系统日志

作者: AI监控团队
版本: 2.0.0
"""

from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    Float, ForeignKey, JSON, Enum, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.schemas import (
    AlertSeverity, AlgorithmType, NotificationChannel, 
    RuleOperator
)


class User(Base):
    """系统用户模型"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    alerts: Mapped[List["Alert"]] = relationship("Alert", foreign_keys="Alert.user_id", back_populates="user")
    rules: Mapped[List["InspectionRule"]] = relationship("InspectionRule", back_populates="user")
    
    __table_args__ = (
        Index('ix_users_username', 'username'),
        Index('ix_users_email', 'email'),
    )


class InspectionRule(Base):
    """巡检规则模型"""
    __tablename__ = "inspection_rules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), nullable=False)
    
    # 条件配置
    conditions: Mapped[Dict] = mapped_column(JSON, nullable=False)  # 存储条件列表
    
    # 通知配置
    notification_channels: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    recipients: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # 执行配置
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    schedule_cron: Mapped[Optional[str]] = mapped_column(String(100))  # Cron表达式
    
    # 标签和分类
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    
    # 关联用户
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    
    # 统计信息
    execution_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    triggered_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_executed: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    user: Mapped[Optional[User]] = relationship("User", back_populates="rules")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="rule")
    
    __table_args__ = (
        Index('ix_inspection_rules_enabled', 'enabled'),
        Index('ix_inspection_rules_severity', 'severity'),
        Index('ix_inspection_rules_category', 'category'),
        Index('ix_inspection_rules_user_id', 'user_id'),
    )


class Alert(Base):
    """告警记录模型"""
    __tablename__ = "alerts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), nullable=False)
    
    # 规则关联
    rule_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("inspection_rules.id"))
    
    # 用户关联
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    
    # 状态管理
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, resolved, acknowledged
    acknowledged_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # 时间信息
    triggered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # 附加信息
    metric_data: Mapped[Optional[Dict]] = mapped_column(JSON)  # 触发告警的指标数据
    context: Mapped[Dict] = mapped_column(JSON, default=dict)  # 告警上下文信息
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    # 关系
    rule: Mapped[Optional[InspectionRule]] = relationship("InspectionRule", back_populates="alerts")
    user: Mapped[Optional[User]] = relationship("User", foreign_keys=[user_id], back_populates="alerts")
    acknowledger: Mapped[Optional[User]] = relationship("User", foreign_keys=[acknowledged_by])
    
    __table_args__ = (
        Index('ix_alerts_severity', 'severity'),
        Index('ix_alerts_status', 'status'),
        Index('ix_alerts_triggered_at', 'triggered_at'),
        Index('ix_alerts_rule_id', 'rule_id'),
        Index('ix_alerts_user_id', 'user_id'),
    )


class Notification(Base):
    """通知记录模型"""
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), nullable=False)
    
    # 渠道信息
    channels: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    recipients: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    
    # 告警关联
    alert_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("alerts.id"))
    
    # 发送状态
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, sent, failed
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    failed_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # 重试机制
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # 附加信息
    extra_data: Mapped[Dict] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    alert: Mapped[Optional[Alert]] = relationship("Alert")
    
    __table_args__ = (
        Index('ix_notifications_status', 'status'),
        Index('ix_notifications_severity', 'severity'),
        Index('ix_notifications_created_at', 'created_at'),
        Index('ix_notifications_alert_id', 'alert_id'),
    )


class Anomaly(Base):
    """异常记录模型"""
    __tablename__ = "anomalies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    algorithm: Mapped[AlgorithmType] = mapped_column(Enum(AlgorithmType), nullable=False)
    
    # 异常信息
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    expected_value: Mapped[float] = mapped_column(Float)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), nullable=False)
    
    # 统计信息
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    deviation: Mapped[float] = mapped_column(Float)
    
    # 关联信息
    alert_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("alerts.id"))
    
    # 附加信息
    labels: Mapped[Dict] = mapped_column(JSON, default=dict)
    context: Mapped[Dict] = mapped_column(JSON, default=dict)
    description: Mapped[Optional[str]] = mapped_column(Text)
    resolution: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    alert: Mapped[Optional[Alert]] = relationship("Alert")
    
    __table_args__ = (
        Index('ix_anomalies_metric_name', 'metric_name'),
        Index('ix_anomalies_algorithm', 'algorithm'),
        Index('ix_anomalies_severity', 'severity'),
        Index('ix_anomalies_timestamp', 'timestamp'),
        Index('ix_anomalies_alert_id', 'alert_id'),
    )


class SystemLog(Base):
    """系统日志模型"""
    __tablename__ = "system_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # info, warning, error, critical
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 上下文信息
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    function: Mapped[Optional[str]] = mapped_column(String(100))
    
    # 附加数据
    data: Mapped[Optional[Dict]] = mapped_column(JSON)
    trace_id: Mapped[Optional[str]] = mapped_column(String(50))
    
    # 关联信息
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    alert_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("alerts.id"))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('ix_system_logs_level', 'level'),
        Index('ix_system_logs_module', 'module'),
        Index('ix_system_logs_created_at', 'created_at'),
        Index('ix_system_logs_user_id', 'user_id'),
        Index('ix_system_logs_alert_id', 'alert_id'),
    )


# 导出所有模型
__all__ = [
    "User",
    "InspectionRule", 
    "Alert",
    "Notification",
    "Anomaly",
    "SystemLog"
]