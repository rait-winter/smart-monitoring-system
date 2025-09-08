#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知服务 - 多渠道智能告警通知系统

负责将监控告警通过多种渠道发送给相关人员，
支持Slack、邮件、Webhook等多种通知方式。

功能特性:
1. 多渠道通知支持 (Slack, Email, Webhook)
2. 模板化消息生成
3. 告警去重和重试机制
4. 发送状态跟踪

作者: AI监控团队
版本: 2.0.0
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

import httpx
import structlog
from jinja2 import Template

from app.models.schemas import (
    NotificationRequest,
    NotificationResponse,
    NotificationStatus,
    NotificationChannel,
    AlertSeverity
)
from app.core.config import settings

logger = structlog.get_logger(__name__)


class NotificationService:
    """
    通知服务 - 多渠道智能告警分发系统
    
    提供统一的通知接口，支持多种通知渠道，
    具备模板化消息、重试机制和状态追踪功能。
    
    核心功能:
    1. 多渠道通知发送 (Slack, Email, Webhook)
    2. 模板化消息生成和个性化定制
    3. 告警去重和重试机制
    4. 发送状态跟踪和统计
    
    使用示例:
        service = NotificationService()
        
        # 发送通知
        response = await service.send_notification(
            title="系统告警",
            message="CPU使用率超过80%",
            severity=AlertSeverity.HIGH,
            channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL]
        )
    """
    
    def __init__(self):
        """初始化通知服务"""
        self.logger = logger.bind(component="NotificationService")
        
        # 通知渠道配置
        self.channel_configs = {
            NotificationChannel.SLACK: {
                "enabled": bool(settings.SLACK_WEBHOOK_URL),
                "webhook_url": settings.SLACK_WEBHOOK_URL,
                "timeout": 10
            },
            NotificationChannel.EMAIL: {
                "enabled": bool(settings.SMTP_HOST),
                "smtp_host": settings.SMTP_HOST,
                "smtp_port": settings.SMTP_PORT,
                "timeout": 30
            },
            NotificationChannel.WEBHOOK: {
                "enabled": True,
                "timeout": 15
            }
        }
        
        # HTTP客户端
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # 通知模板
        self.templates = {
            AlertSeverity.LOW: "⚠️ [低级别告警] {{ title }}\n{{ message }}\n时间: {{ timestamp }}",
            AlertSeverity.MEDIUM: "🟡 [中等告警] {{ title }}\n{{ message }}\n时间: {{ timestamp }}\n请及时关注。",
            AlertSeverity.HIGH: "🔴 [高级别告警] {{ title }}\n{{ message }}\n时间: {{ timestamp }}\n⚠️ 请立即处理！",
            AlertSeverity.CRITICAL: "🚨 [严重告警] {{ title }}\n{{ message }}\n时间: {{ timestamp }}\n🚨 需要立即处理！"
        }
        
        # 通知统计
        self.notification_stats = {
            "total_sent": 0,
            "successful_sent": 0,
            "failed_sent": 0
        }
        
        # 去重配置
        self.dedup_window = timedelta(minutes=5)
        self.recent_notifications = {}
        
        self.logger.info(
            "通知服务初始化完成",
            enabled_channels=[ch.value for ch, config in self.channel_configs.items() if config["enabled"]]
        )
    
    
    async def send_notification(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        channels: List[NotificationChannel],
        recipients: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> NotificationResponse:
        """
        发送单个通知
        
        Args:
            title: 通知标题
            message: 通知内容
            severity: 严重程度
            channels: 通知渠道列表
            recipients: 接收人列表
            metadata: 附加元数据
            
        Returns:
            NotificationResponse: 发送结果
        """
        notification_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            self.logger.info(
                "开始发送通知",
                notification_id=notification_id,
                title=title,
                severity=severity.value,
                channels=[ch.value for ch in channels]
            )
            
            # 检查去重
            if await self._is_duplicate_notification(title, message, severity):
                return NotificationResponse(
                    success=True,
                    message="通知已去重，跳过发送",
                    notification_id=notification_id,
                    statuses={}
                )
            
            # 渲染通知内容
            rendered_content = await self._render_content(title, message, severity, metadata)
            
            # 并发发送到各个渠道
            statuses = {}
            successful_channels = 0
            
            for channel in channels:
                if self.channel_configs[channel]["enabled"]:
                    try:
                        status = await self._send_to_channel(
                            channel, rendered_content, recipients, notification_id
                        )
                        statuses[channel.value] = status
                        if status.status == "sent":
                            successful_channels += 1
                    except Exception as e:
                        statuses[channel.value] = NotificationStatus(
                            notification_id=notification_id,
                            channel=channel,
                            status="failed",
                            error_message=str(e)
                        )
                else:
                    self.logger.warning("通知渠道未启用", channel=channel.value)
            
            # 更新统计
            self.notification_stats["total_sent"] += 1
            if successful_channels > 0:
                self.notification_stats["successful_sent"] += 1
            else:
                self.notification_stats["failed_sent"] += 1
            
            # 记录去重信息
            await self._record_notification(title, message, severity)
            
            execution_time = time.time() - start_time
            is_success = successful_channels > 0
            
            self.logger.info(
                "通知发送完成",
                notification_id=notification_id,
                successful_channels=successful_channels,
                total_channels=len(channels),
                execution_time=round(execution_time, 3),
                success=is_success
            )
            
            return NotificationResponse(
                success=is_success,
                message=f"通知发送完成，成功{successful_channels}/{len(channels)}个渠道",
                notification_id=notification_id,
                statuses=statuses
            )
            
        except Exception as e:
            self.logger.error("通知发送失败", notification_id=notification_id, error=str(e))
            self.notification_stats["total_sent"] += 1
            self.notification_stats["failed_sent"] += 1
            raise RuntimeError(f"通知发送失败: {str(e)}")
    
    
    async def send_notification_request(self, request: NotificationRequest) -> NotificationResponse:
        """
        发送通知请求
        
        Args:
            request: 通知请求数据
            
        Returns:
            NotificationResponse: 发送结果
        """
        return await self.send_notification(
            title=request.title,
            message=request.message,
            severity=request.severity,
            channels=request.channels,
            recipients=request.recipients,
            metadata=request.metadata
        )

    async def _render_content(
        self, 
        title: str, 
        message: str, 
        severity: AlertSeverity, 
        metadata: Optional[Dict[str, Any]]
    ) -> str:
        """渲染通知内容"""
        try:
            template_str = self.templates.get(severity, self.templates[AlertSeverity.MEDIUM])
            template = Template(template_str)
            
            return template.render(
                title=title,
                message=message,
                severity=severity.value.upper(),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                metadata=metadata or {}
            )
        except Exception as e:
            self.logger.error("内容渲染失败", error=str(e))
            return f"[{severity.value.upper()}] {title}\n{message}\n时间: {datetime.now()}"
    
    
    async def _send_to_channel(
        self,
        channel: NotificationChannel,
        content: str,
        recipients: Optional[List[str]],
        notification_id: str
    ) -> NotificationStatus:
        """发送通知到指定渠道"""
        try:
            if channel == NotificationChannel.SLACK:
                return await self._send_slack(content, notification_id)
            elif channel == NotificationChannel.EMAIL:
                return await self._send_email(content, recipients, notification_id)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(content, recipients, notification_id)
            else:
                raise ValueError(f"不支持的通知渠道: {channel}")
        except Exception as e:
            return NotificationStatus(
                notification_id=notification_id,
                channel=channel,
                status="failed",
                error_message=str(e)
            )
    
    
    async def _send_slack(self, content: str, notification_id: str) -> NotificationStatus:
        """发送Slack通知"""
        config = self.channel_configs[NotificationChannel.SLACK]
        
        if not config["webhook_url"]:
            raise RuntimeError("Slack Webhook URL未配置")
        
        payload = {"text": content}
        
        response = await self.http_client.post(
            str(config["webhook_url"]),
            json=payload,
            timeout=config["timeout"]
        )
        response.raise_for_status()
        
        return NotificationStatus(
            notification_id=notification_id,
            channel=NotificationChannel.SLACK,
            status="sent",
            sent_at=datetime.now()
        )
    
    
    async def _send_email(
        self, 
        content: str, 
        recipients: Optional[List[str]], 
        notification_id: str
    ) -> NotificationStatus:
        """
        发送邮件通知
        
        Args:
            content: 邮件内容
            recipients: 收件人列表
            notification_id: 通知ID
            
        Returns:
            NotificationStatus: 发送状态
        """
        try:
            # 检查SMTP配置
            if not settings.SMTP_HOST:
                raise RuntimeError("SMTP服务器未配置")
            
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.utils import formatdate
            
            # 创建邮件内容
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_USERNAME
            msg['To'] = ', '.join(recipients) if recipients else settings.SMTP_USERNAME
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = "智能监控预警系统通知"
            
            # 添加文本内容
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 发送邮件
            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS
            )
            
            return NotificationStatus(
                notification_id=notification_id,
                channel=NotificationChannel.EMAIL,
                status="sent",
                sent_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error("邮件发送失败", error=str(e))
            return NotificationStatus(
                notification_id=notification_id,
                channel=NotificationChannel.EMAIL,
                status="failed",
                error_message=str(e)
            )

    async def _send_webhook(
        self, 
        content: str, 
        recipients: Optional[List[str]], 
        notification_id: str
    ) -> NotificationStatus:
        """
        发送Webhook通知
        
        Args:
            content: 通知内容
            recipients: Webhook URL列表
            notification_id: 通知ID
            
        Returns:
            NotificationStatus: 发送状态
        """
        try:
            if not recipients:
                raise ValueError("Webhook URL列表为空")
            
            # 构造通知数据
            payload = {
                "notification_id": notification_id,
                "message": content,
                "timestamp": datetime.now().isoformat(),
                "source": "smart-monitoring-system"
            }
            
            # 发送到所有URL
            success_count = 0
            last_error = None
            
            for webhook_url in recipients:
                try:
                    response = await self.http_client.post(
                        webhook_url,
                        json=payload,
                        timeout=self.channel_configs[NotificationChannel.WEBHOOK]["timeout"]
                    )
                    response.raise_for_status()
                    success_count += 1
                except Exception as e:
                    last_error = e
                    self.logger.warning("Webhook发送失败", url=webhook_url, error=str(e))
            
            if success_count > 0:
                return NotificationStatus(
                    notification_id=notification_id,
                    channel=NotificationChannel.WEBHOOK,
                    status="sent",
                    sent_at=datetime.now()
                )
            else:
                raise last_error or RuntimeError("所有Webhook发送都失败")
                
        except Exception as e:
            self.logger.error("Webhook发送失败", error=str(e))
            return NotificationStatus(
                notification_id=notification_id,
                channel=NotificationChannel.WEBHOOK,
                status="failed",
                error_message=str(e)
            )

    
    async def _is_duplicate_notification(self, title: str, message: str, severity: AlertSeverity) -> bool:
        """检查是否为重复通知"""
        dedup_key = f"{title}:{message}:{severity.value}"
        
        # 清理过期记录
        now = datetime.now()
        cutoff_time = now - self.dedup_window
        
        expired_keys = [
            key for key, timestamp in self.recent_notifications.items()
            if timestamp < cutoff_time
        ]
        for key in expired_keys:
            del self.recent_notifications[key]
        
        return dedup_key in self.recent_notifications
    
    
    async def _record_notification(self, title: str, message: str, severity: AlertSeverity) -> None:
        """记录通知用于去重"""
        dedup_key = f"{title}:{message}:{severity.value}"
        self.recent_notifications[dedup_key] = datetime.now()
    
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取通知统计信息"""
        return {
            "total_stats": self.notification_stats.copy(),
            "channel_availability": {
                channel.value: config["enabled"]
                for channel, config in self.channel_configs.items()
            },
            "dedup_stats": {
                "active_dedups": len(self.recent_notifications),
                "dedup_window_minutes": self.dedup_window.total_seconds() / 60
            }
        }
    
    
    async def test_channels(self) -> Dict[str, bool]:
        """测试所有通知渠道的可用性"""
        test_results = {}
        
        for channel in NotificationChannel:
            if not self.channel_configs[channel]["enabled"]:
                test_results[channel.value] = False
                continue
            
            try:
                test_content = f"[测试] 监控系统通知渠道测试\n发送时间: {datetime.now()}"
                test_recipients = ["test@example.com"] if channel == NotificationChannel.EMAIL else ["http://example.com/webhook"]
                
                status = await self._send_to_channel(
                    channel,
                    test_content,
                    test_recipients,
                    f"test-{channel.value}-{int(time.time())}"
                )
                
                test_results[channel.value] = status.status == "sent"
                
            except Exception as e:
                self.logger.error(f"渠道{channel.value}测试失败", error=str(e))
                test_results[channel.value] = False
        
        return test_results
    
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.http_client.aclose()


# 导出类
__all__ = ["NotificationService"]