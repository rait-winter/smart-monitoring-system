"""
系统日志相关的API端点
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime, timedelta

from app.models.schemas import APIResponse

logger = structlog.get_logger(__name__)

# 创建路由器
router = APIRouter()

# 模拟日志数据存储
def generate_sample_logs(count: int = 100) -> List[Dict[str, Any]]:
    """生成示例日志数据"""
    levels = ["INFO", "WARNING", "ERROR", "SUCCESS", "DEBUG"]
    users = ["system", "admin", "operator", "viewer"]
    messages = [
        "用户登录系统",
        "通知服务响应缓慢",
        "Redis服务连接失败",
        "创建新的监控规则",
        "系统备份完成",
        "缓存清理完成",
        "数据库连接超时",
        "配置更新完成",
        "CPU使用率较高",
        "服务重启成功",
        "磁盘空间不足",
        "内存使用率过高",
        "网络连接异常",
        "定时任务执行成功",
        "数据同步完成",
        "安全扫描完成",
        "日志清理完成",
        "性能监控告警",
        "用户权限变更",
        "系统版本更新"
    ]
    
    logs = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(count):
        log_time = base_time + timedelta(minutes=i * 5)
        logs.append({
            "id": i + 1,
            "timestamp": log_time.strftime("%Y-%m-%d %H:%M:%S"),
            "level": levels[i % len(levels)],
            "user": users[i % len(users)],
            "message": messages[i % len(messages)]
        })
    
    # 按时间倒序排列
    logs.reverse()
    return logs

# 全局日志存储
logs_db = generate_sample_logs(200)


@router.get("/", response_model=APIResponse)
async def get_system_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    level: Optional[str] = Query(None, description="日志级别过滤"),
    user: Optional[str] = Query(None, description="用户过滤"),
    search: Optional[str] = Query(None, description="搜索关键词")
) -> APIResponse:
    """获取系统日志"""
    try:
        # 过滤日志
        filtered_logs = logs_db.copy()
        
        # 按级别过滤
        if level:
            filtered_logs = [log for log in filtered_logs if log["level"] == level]
        
        # 按用户过滤
        if user:
            filtered_logs = [log for log in filtered_logs if log["user"] == user]
        
        # 按关键词搜索
        if search:
            search_lower = search.lower()
            filtered_logs = [
                log for log in filtered_logs 
                if search_lower in log["message"].lower() or search_lower in log["user"].lower()
            ]
        
        # 分页
        total = len(filtered_logs)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_logs = filtered_logs[start:end]
        
        return APIResponse(
            success=True,
            message=f"获取到 {len(paginated_logs)} 条日志",
            data={
                "logs": paginated_logs,
                "pagination": {
                    "page": page,
                    "pageSize": page_size,
                    "total": total,
                    "totalPages": (total + page_size - 1) // page_size
                }
            }
        )
        
    except Exception as e:
        logger.error("获取系统日志失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"获取系统日志失败: {str(e)}")


@router.delete("/", response_model=APIResponse)
async def clear_system_logs() -> APIResponse:
    """清空系统日志"""
    try:
        global logs_db
        cleared_count = len(logs_db)
        logs_db = []
        
        logger.info("系统日志已清空", cleared_count=cleared_count)
        
        return APIResponse(
            success=True,
            message=f"已清空 {cleared_count} 条日志",
            data={"clearedCount": cleared_count}
        )
        
    except Exception as e:
        logger.error("清空系统日志失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"清空系统日志失败: {str(e)}")


@router.post("/refresh", response_model=APIResponse)
async def refresh_system_logs() -> APIResponse:
    """刷新系统日志"""
    try:
        global logs_db
        
        # 模拟获取最新日志
        new_logs = generate_sample_logs(50)
        
        # 添加新日志到开头
        logs_db = new_logs + logs_db
        
        # 限制总数量，保留最新的1000条
        if len(logs_db) > 1000:
            logs_db = logs_db[:1000]
        
        logger.info("系统日志已刷新", new_count=len(new_logs), total_count=len(logs_db))
        
        return APIResponse(
            success=True,
            message=f"已刷新日志，获取到 {len(new_logs)} 条新日志",
            data={
                "newCount": len(new_logs),
                "totalCount": len(logs_db)
            }
        )
        
    except Exception as e:
        logger.error("刷新系统日志失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"刷新系统日志失败: {str(e)}")


@router.get("/stats", response_model=APIResponse)
async def get_log_statistics() -> APIResponse:
    """获取日志统计信息"""
    try:
        # 统计各级别日志数量
        level_stats = {}
        user_stats = {}
        
        for log in logs_db:
            level = log["level"]
            user = log["user"]
            
            level_stats[level] = level_stats.get(level, 0) + 1
            user_stats[user] = user_stats.get(user, 0) + 1
        
        # 最近24小时日志数量
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        recent_logs = [
            log for log in logs_db 
            if datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S") >= yesterday
        ]
        
        return APIResponse(
            success=True,
            message="日志统计信息获取成功",
            data={
                "totalLogs": len(logs_db),
                "recentLogs": len(recent_logs),
                "levelStats": level_stats,
                "userStats": user_stats
            }
        )
        
    except Exception as e:
        logger.error("获取日志统计失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"获取日志统计失败: {str(e)}")

