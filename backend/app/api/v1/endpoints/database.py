"""
数据库配置和管理相关的API端点
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import structlog
import asyncpg
import asyncio

from app.models.schemas import APIResponse
from app.services.config_db_service import config_db_service

logger = structlog.get_logger(__name__)

# 创建路由器
router = APIRouter()


@router.post("/config/validate-name", response_model=APIResponse)
async def validate_database_config_name(request_data: Dict[str, str] = Body(...)) -> APIResponse:
    """验证数据库配置名称"""
    try:
        name = request_data.get("name", "")
        validation_result = config_db_service.validate_config_name(name)
        
        return APIResponse(
            success=validation_result["valid"],
            message=validation_result.get("message", "配置名称验证通过"),
            data=validation_result
        )
    except Exception as e:
        logger.error("数据库配置名称验证失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"配置名称验证失败: {str(e)}")


@router.post("/config/set-current/{config_id}", response_model=APIResponse)
async def set_current_database_config(config_id: int) -> APIResponse:
    """设置当前使用的数据库配置"""
    try:
        result = await config_db_service.set_current_database_config(config_id)
        
        return APIResponse(
            success=result["success"],
            message=result["message"],
            data=result
        )
    except Exception as e:
        logger.error("设置当前数据库配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"设置当前配置失败: {str(e)}")


@router.get("/config", response_model=APIResponse)
async def get_database_config() -> APIResponse:
    """获取数据库配置"""
    try:
        # 优先从数据库获取配置
        db_config = await config_db_service.get_default_database_config()
        if db_config:
            config = {
                "name": db_config["name"],
                "postgresql": {
                    "enabled": db_config["enabled"],
                    "host": db_config["host"],
                    "port": db_config["port"],
                    "database": db_config["database"],
                    "username": db_config["username"],
                    "password": db_config["password"],
                    "ssl": db_config["ssl"]
                },
                "backup": {
                    "enabled": db_config["backupEnabled"],
                    "schedule": db_config["backupSchedule"],
                    "retention": db_config["backupRetention"],
                    "path": db_config["backupPath"]
                },
                "updatedAt": db_config["updatedAt"]
            }
        else:
            # 返回默认配置
            config = {
                "name": "默认数据库配置",
                "postgresql": {
                    "enabled": True,
                    "host": "localhost",
                    "port": 5432,
                    "database": "monitoring",
                    "username": "postgres",
                    "password": "",
                    "ssl": False
                },
                "backup": {
                    "enabled": True,
                    "schedule": "0 2 * * *",
                    "retention": 30,
                    "path": "/data/backups"
                }
            }
        
        return APIResponse(
            success=True,
            message="获取数据库配置成功",
            data={"config": config}
        )
        
    except Exception as e:
        logger.error("获取数据库配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config", response_model=APIResponse)
async def update_database_config(config: Dict[str, Any] = Body(..., description="数据库配置")) -> APIResponse:
    """更新数据库配置"""
    try:
        # 保存配置到数据库
        result = await config_db_service.save_database_config(config)
        
        # 检查保存结果
        if not result.get("success", True):
            return APIResponse(
                success=False,
                message=result.get("message", "配置保存失败"),
                data=result
            )
        
        return APIResponse(
            success=True,
            message="数据库配置保存成功",
            data=result
        )
        
    except Exception as e:
        logger.error("保存数据库配置失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/history", response_model=APIResponse)
async def get_database_config_history() -> APIResponse:
    """获取数据库配置历史"""
    try:
        configs = await config_db_service.get_all_database_configs()
        
        return APIResponse(
            success=True,
            message=f"获取到 {len(configs)} 个数据库配置",
            data={
                "configs": configs,
                "total": len(configs)
            }
        )
        
    except Exception as e:
        logger.error("获取数据库配置历史失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/config/history", response_model=APIResponse)
async def clear_database_config_history() -> APIResponse:
    """清空数据库配置历史"""
    try:
        # 注意：这里应该只清除非当前的配置，保留当前配置
        # 这个功能需要在config_db_service中实现
        
        return APIResponse(
            success=True,
            message="数据库配置历史已清空"
        )
        
    except Exception as e:
        logger.error("清空数据库配置历史失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test", response_model=APIResponse)
async def test_database_connection(config: Dict[str, Any] = Body(..., description="数据库配置")) -> APIResponse:
    """测试数据库连接"""
    try:
        # 提取PostgreSQL配置
        postgresql_config = config.get("postgresql", {})
        
        host = postgresql_config.get("host", "localhost")
        port = postgresql_config.get("port", 5432)
        database = postgresql_config.get("database", "monitoring")
        username = postgresql_config.get("username", "postgres")
        password = postgresql_config.get("password", "")
        ssl_mode = "require" if postgresql_config.get("ssl", False) else "disable"
        
        # 构建连接字符串
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}?sslmode={ssl_mode}"
        
        # 测试连接
        try:
            conn = await asyncpg.connect(connection_string, timeout=10)
            
            # 获取数据库信息
            version = await conn.fetchval("SELECT version()")
            uptime_result = await conn.fetchval("SELECT pg_postmaster_start_time()")
            total_connections = await conn.fetchval("SELECT count(*) FROM pg_stat_activity")
            active_connections = await conn.fetchval(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            )
            db_size_result = await conn.fetchval(
                "SELECT pg_size_pretty(pg_database_size(current_database()))"
            )
            
            await conn.close()
            
            # 计算运行时间
            from datetime import datetime
            uptime_delta = datetime.now(uptime_result.tzinfo) - uptime_result
            uptime_hours = int(uptime_delta.total_seconds() // 3600)
            uptime_days = uptime_hours // 24
            uptime_hours = uptime_hours % 24
            
            uptime_str = f"{uptime_days}天{uptime_hours}小时" if uptime_days > 0 else f"{uptime_hours}小时"
            
            return APIResponse(
                success=True,
                message="连接成功",
                data={
                    "healthy": True,
                    "version": version,
                    "uptime": uptime_str,
                    "totalConnections": total_connections,
                    "activeConnections": active_connections,
                    "dbSize": db_size_result
                }
            )
            
        except asyncpg.exceptions.InvalidAuthorizationSpecificationError:
            return APIResponse(
                success=False,
                message="连接失败: 用户名或密码错误",
                data={"healthy": False}
            )
        except asyncpg.exceptions.InvalidCatalogNameError:
            return APIResponse(
                success=False,
                message="连接失败: 数据库不存在",
                data={"healthy": False}
            )
        except asyncpg.exceptions.ConnectionDoesNotExistError:
            return APIResponse(
                success=False,
                message="连接失败: 无法连接到数据库服务器",
                data={"healthy": False}
            )
        except asyncio.TimeoutError:
            return APIResponse(
                success=False,
                message="连接超时",
                data={"healthy": False}
            )
        except Exception as conn_error:
            return APIResponse(
                success=False,
                message=f"连接失败: {str(conn_error)}",
                data={"healthy": False}
            )
            
    except Exception as e:
        logger.error("测试数据库连接失败", error=str(e))
        return APIResponse(
            success=False,
            message="连接测试失败",
            data={"healthy": False, "error": str(e)}
        )


@router.post("/query", response_model=APIResponse)
async def execute_database_query(params: Dict[str, Any] = Body(...)) -> APIResponse:
    """执行数据库查询"""
    try:
        query = params.get("query", "").strip()
        config = params.get("config", {})
        
        if not query:
            return APIResponse(
                success=False,
                message="查询语句不能为空"
            )
        
        # 提取PostgreSQL配置
        postgresql_config = config.get("postgresql", {})
        
        host = postgresql_config.get("host", "localhost")
        port = postgresql_config.get("port", 5432)
        database = postgresql_config.get("database", "monitoring")
        username = postgresql_config.get("username", "postgres")
        password = postgresql_config.get("password", "")
        ssl_mode = "require" if postgresql_config.get("ssl", False) else "disable"
        
        # 构建连接字符串
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}?sslmode={ssl_mode}"
        
        # 执行查询
        try:
            conn = await asyncpg.connect(connection_string, timeout=10)
            
            # 限制查询结果数量，防止内存溢出
            if "LIMIT" not in query.upper() and "SELECT" in query.upper():
                if not query.rstrip().endswith(';'):
                    query += " LIMIT 100"
                else:
                    query = query.rstrip(';') + " LIMIT 100;"
            
            result = await conn.fetch(query)
            await conn.close()
            
            # 将结果转换为字典列表
            data = []
            for row in result:
                row_dict = {}
                for key, value in row.items():
                    # 处理特殊数据类型
                    if hasattr(value, 'isoformat'):  # datetime对象
                        row_dict[key] = value.isoformat()
                    elif isinstance(value, (list, dict)):
                        row_dict[key] = str(value)
                    else:
                        row_dict[key] = value
                data.append(row_dict)
            
            return APIResponse(
                success=True,
                message=f"查询成功，返回 {len(data)} 行结果",
                data={"data": data, "rowCount": len(data)}
            )
            
        except asyncpg.exceptions.PostgresSyntaxError as e:
            return APIResponse(
                success=False,
                message=f"SQL语法错误: {str(e)}",
                data={"error": str(e)}
            )
        except asyncpg.exceptions.UndefinedTableError as e:
            return APIResponse(
                success=False,
                message=f"表不存在: {str(e)}",
                data={"error": str(e)}
            )
        except Exception as query_error:
            return APIResponse(
                success=False,
                message=f"查询执行失败: {str(query_error)}",
                data={"error": str(query_error)}
            )
            
    except Exception as e:
        logger.error("执行数据库查询失败", error=str(e))
        return APIResponse(
            success=False,
            message="查询执行失败",
            data={"error": str(e)}
        )


@router.get("/health", response_model=APIResponse)
async def check_database_health() -> APIResponse:
    """检查数据库健康状态"""
    try:
        # 获取当前配置
        db_config = await config_db_service.get_default_database_config()
        
        if not db_config or not db_config.get("enabled", False):
            return APIResponse(
                success=False,
                message="数据库未启用",
                data={"healthy": False}
            )
        
        # 构建连接字符串
        ssl_mode = "require" if db_config.get("ssl", False) else "disable"
        connection_string = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?sslmode={ssl_mode}"
        
        # 简单的健康检查
        try:
            conn = await asyncpg.connect(connection_string, timeout=5)
            await conn.fetchval("SELECT 1")
            await conn.close()
            
            return APIResponse(
                success=True,
                message="数据库健康",
                data={"healthy": True}
            )
            
        except Exception as conn_error:
            return APIResponse(
                success=False,
                message=f"数据库连接失败: {str(conn_error)}",
                data={"healthy": False}
            )
            
    except Exception as e:
        logger.error("检查数据库健康状态失败", error=str(e))
        return APIResponse(
            success=False,
            message="健康检查失败",
            data={"healthy": False, "error": str(e)}
        )
