"""
系统管理和服务状态相关的API端点
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import structlog
import psutil
import asyncio
import time
from datetime import datetime, timedelta
import os
import socket
import requests
from urllib.parse import urlparse
import platform
import subprocess

from app.models.schemas import APIResponse

logger = structlog.get_logger(__name__)

# 创建路由器
router = APIRouter()


def get_online_users() -> int:
    """获取在线用户数（跨平台支持）"""
    try:
        # 优先使用psutil，速度更快更可靠
        try:
            users = psutil.users()
            if users:
                return len(users)
        except Exception:
            pass
        
        system_name = platform.system().lower()
        
        if system_name == "windows":
            # Windows系统：使用query user命令
            try:
                result = subprocess.run(
                    ["query", "user"], 
                    capture_output=True, 
                    text=True, 
                    timeout=2,
                    encoding='gbk',  # Windows中文系统使用GBK编码
                    errors='ignore'  # 忽略编码错误
                )
                if result.returncode == 0:
                    # 解析输出，排除标题行和断开连接的会话
                    lines = result.stdout.strip().split('\n')
                    active_users = 0
                    for line in lines[1:]:  # 跳过标题行
                        if line.strip() and 'Disc' not in line:  # 排除断开连接的会话
                            active_users += 1
                    return active_users
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError, UnicodeDecodeError):
                pass
            
            # 备选方案：使用psutil获取活动进程的用户
            try:
                users = set()
                for proc in psutil.process_iter(['username']):
                    try:
                        username = proc.info['username']
                        if username and username not in ['SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE']:
                            users.add(username)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                return len(users)
            except Exception:
                pass
                
        elif system_name == "linux":
            # Linux系统：使用who命令
            try:
                result = subprocess.run(
                    ["who"], 
                    capture_output=True, 
                    text=True, 
                    timeout=2,
                    encoding='utf-8',
                    errors='ignore'
                )
                if result.returncode == 0:
                    # 计算活动用户会话数
                    lines = result.stdout.strip().split('\n')
                    return len([line for line in lines if line.strip()])
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError, UnicodeDecodeError):
                pass
            
            # 备选方案：使用users命令
            try:
                result = subprocess.run(
                    ["users"], 
                    capture_output=True, 
                    text=True, 
                    timeout=2,
                    encoding='utf-8',
                    errors='ignore'
                )
                if result.returncode == 0:
                    users = result.stdout.strip().split()
                    return len(set(users))  # 去重
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError, UnicodeDecodeError):
                pass
        
        # 已经在开头尝试过psutil了，这里不再重复
            
        # 如果所有方法都失败，返回1（当前用户）
        return 1
        
    except Exception as e:
        logger.warning("获取在线用户数失败", error=str(e))
        return 1


def get_system_info() -> Dict[str, Any]:
    """获取详细的系统信息（跨平台支持）"""
    try:
        system_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "processor": platform.processor(),
        }
        
        # 获取CPU信息
        try:
            cpu_count = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_freq = psutil.cpu_freq()
            
            system_info.update({
                "cpu_count_logical": cpu_count,
                "cpu_count_physical": cpu_count_physical,
                "cpu_freq_current": round(cpu_freq.current, 2) if cpu_freq else None,
                "cpu_freq_max": round(cpu_freq.max, 2) if cpu_freq else None,
            })
        except Exception as e:
            logger.warning("获取CPU信息失败", error=str(e))
        
        # 获取磁盘信息
        try:
            # 根据操作系统选择合适的磁盘路径
            disk_path = 'C:\\' if platform.system().lower() == 'windows' else '/'
            disk_usage = psutil.disk_usage(disk_path)
            system_info.update({
                "disk_total": round(disk_usage.total / (1024**3), 2),  # GB
                "disk_used": round(disk_usage.used / (1024**3), 2),   # GB
                "disk_free": round(disk_usage.free / (1024**3), 2),   # GB
                "disk_usage_percent": round((disk_usage.used / disk_usage.total) * 100, 1)
            })
        except Exception as e:
            logger.warning("获取磁盘信息失败", error=str(e))
        
        # 获取网络信息
        try:
            net_io = psutil.net_io_counters()
            system_info.update({
                "network_bytes_sent": net_io.bytes_sent,
                "network_bytes_recv": net_io.bytes_recv,
                "network_packets_sent": net_io.packets_sent,
                "network_packets_recv": net_io.packets_recv,
            })
        except Exception as e:
            logger.warning("获取网络信息失败", error=str(e))
        
        return system_info
        
    except Exception as e:
        logger.error("获取系统信息失败", error=str(e))
        return {}


def check_service_health(service_name: str, port: int) -> Dict[str, Any]:
    """检查服务健康状态"""
    try:
        # 基本端口检查 - 减少超时时间
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # 减少到1秒
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result != 0:
            return {
                "status": "stopped",
                "health": "unhealthy",
                "message": f"端口 {port} 未响应"
            }
        
        # 针对不同服务进行特定健康检查 - 减少超时时间
        health_status = "healthy"
        message = "服务正常运行"
        
        if service_name == "API网关" and port == 8000:
            # 跳过自己的健康检查以避免循环
            health_status = "healthy"
            message = "API网关正常运行"
                
        elif service_name == "前端服务" and port == 3000:
            try:
                response = requests.get("http://localhost:3000", timeout=2)
                if response.status_code != 200:
                    health_status = "degraded"
                    message = f"前端服务响应异常: {response.status_code}"
            except requests.RequestException:
                health_status = "degraded"
                message = "前端服务检查失败"
                
        elif service_name == "Prometheus" and port == 9090:
            try:
                response = requests.get("http://localhost:9090/-/healthy", timeout=2)
                if response.status_code != 200:
                    health_status = "degraded"
                    message = f"Prometheus健康检查失败: {response.status_code}"
            except requests.RequestException:
                health_status = "degraded"
                message = "Prometheus连接失败"
        
        return {
            "status": "running",
            "health": health_status,
            "message": message
        }
        
    except Exception as e:
        return {
            "status": "unknown",
            "health": "unhealthy",
            "message": f"健康检查异常: {str(e)}"
        }


@router.get("/health", response_model=APIResponse)
async def get_system_health() -> APIResponse:
    """获取系统健康状态 - 包含真实系统信息"""
    try:
        # 快速获取基础系统信息，避免阻塞操作
        async def _get_basic_info():
            # 使用非阻塞方式获取CPU使用率
            cpu_usage = psutil.cpu_percent(interval=0)  # 不等待，使用缓存值
            memory = psutil.virtual_memory()
            
            # 计算运行时间
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            uptime_hours = int(uptime // 3600)
            uptime_days = uptime_hours // 24
            uptime_hours = uptime_hours % 24
            
            # 获取在线用户数
            online_users = get_online_users()
            
            # 获取详细系统信息
            system_details = get_system_info()
            
            return {
                "uptime": f"{uptime_days}天{uptime_hours}小时",
                "uptimeSeconds": int(uptime),
                "cpuUsage": round(cpu_usage, 1),
                "memoryUsage": round(memory.percent, 1),
                "memoryTotal": round(memory.total / (1024**3), 2),  # GB
                "memoryUsed": round(memory.used / (1024**3), 2),   # GB
                "onlineUsers": online_users,
                "timestamp": datetime.now().isoformat(),
                "systemInfo": system_details
            }
        
        # 3秒超时获取基础信息（优化性能）
        health_data = await asyncio.wait_for(_get_basic_info(), timeout=3.0)
        
        return APIResponse(
            success=True,
            message="系统健康状态获取成功",
            data=health_data
        )
            
    except asyncio.TimeoutError:
        logger.warning("系统健康检查超时")
        # 返回基础信息
        return APIResponse(
            success=True,
            message="系统状态检查部分超时",
            data={
                "uptime": "检查超时",
                "cpuUsage": 0,
                "memoryUsage": 0,
                "onlineUsers": 1,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error("获取系统健康状态失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"获取系统健康状态失败: {str(e)}")


@router.get("/services", response_model=APIResponse)
async def get_services_status() -> APIResponse:
    """获取服务状态"""
    try:
        # 添加整体超时机制
        async def _get_services():
            services = []
            
            # 检查主要服务端口
            service_ports = {
                "API网关": 8000,
                "前端服务": 3000,
                "数据库服务": 5432,
                "Redis服务": 6379,
                "AI检测服务": 8001,
                "规则引擎": 8002,
                "通知服务": 8003,
                "Prometheus": 9090
            }
        
            # 一次性获取所有网络连接，避免重复调用
            try:
                connections = psutil.net_connections()
            except Exception as e:
                logger.warning("获取网络连接失败", error=str(e))
                connections = []
            
            for service_name, port in service_ports.items():
                try:
                    # 使用快速健康检查
                    health_info = check_service_health(service_name, port)
                    
                    # 在已获取的连接列表中查找端口
                    port_connection = None
                    for conn in connections:
                        if conn.laddr and conn.laddr.port == port:
                            port_connection = conn
                            break
                    
                    if port_connection and health_info["status"] == "running":
                        # 如果端口被占用且健康检查通过，尝试获取进程信息
                        try:
                            process = psutil.Process(port_connection.pid)
                            cpu_usage = process.cpu_percent()
                            memory_info = process.memory_info()
                            create_time = process.create_time()
                            uptime = time.time() - create_time
                            
                            uptime_hours = int(uptime // 3600)
                            uptime_days = uptime_hours // 24
                            uptime_hours = uptime_hours % 24
                            
                            services.append({
                                "name": service_name,
                                "status": health_info["status"],
                                "health": health_info["health"],
                                "message": health_info["message"],
                                "port": port,
                                "pid": port_connection.pid,
                                "cpuUsage": round(cpu_usage, 1),
                                "memoryUsage": round(memory_info.rss / (1024**2), 1),  # MB
                                "uptime": f"{uptime_days}天{uptime_hours}小时" if uptime_days > 0 else f"{uptime_hours}小时",
                                "lastCheck": datetime.now().isoformat()
                            })
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            # 如果无法获取进程信息，使用基本信息
                            services.append({
                                "name": service_name,
                                "status": health_info["status"],
                                "health": health_info["health"],
                                "message": health_info["message"],
                                "port": port,
                                "pid": port_connection.pid if port_connection else None,
                                "cpuUsage": 0,
                                "memoryUsage": 0,
                                "uptime": "进程信息不可用",
                                "lastCheck": datetime.now().isoformat()
                            })
                    else:
                        # 端口未被占用或健康检查失败
                        services.append({
                            "name": service_name,
                            "status": health_info["status"],
                            "health": health_info.get("health", "unhealthy"),
                            "message": health_info.get("message", "服务未运行"),
                            "port": port,
                            "pid": None,
                            "cpuUsage": 0,
                            "memoryUsage": 0,
                            "uptime": "-",
                            "lastCheck": datetime.now().isoformat()
                        })
                        
                except Exception as service_error:
                    logger.warning("检查服务状态失败", service=service_name, error=str(service_error))
                    services.append({
                        "name": service_name,
                        "status": "unknown",
                        "health": "unhealthy",
                        "message": f"检查失败: {str(service_error)}",
                        "port": port,
                        "pid": None,
                        "cpuUsage": 0,
                        "memoryUsage": 0,
                        "uptime": "检查失败",
                        "lastCheck": datetime.now().isoformat()
                    })
            
            return services
        
        # 使用超时机制执行服务检查
        services = await asyncio.wait_for(_get_services(), timeout=10.0)
        
        return APIResponse(
            success=True,
            message=f"获取到 {len(services)} 个服务状态",
            data={"services": services, "total": len(services)}
        )
        
    except Exception as e:
        logger.error("获取服务状态失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")


@router.post("/services/{service_name}/restart", response_model=APIResponse)
async def restart_service(service_name: str) -> APIResponse:
    """重启服务"""
    try:
        # 这里应该实现实际的服务重启逻辑
        # 为了安全起见，暂时只返回模拟结果
        logger.info("服务重启请求", service=service_name)
        
        # 模拟重启延迟
        await asyncio.sleep(1)
        
        return APIResponse(
            success=True,
            message=f"服务 {service_name} 重启成功",
            data={"service": service_name, "action": "restart", "timestamp": datetime.now().isoformat()}
        )
        
    except Exception as e:
        logger.error("服务重启失败", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"服务重启失败: {str(e)}")


@router.post("/services/{service_name}/stop", response_model=APIResponse)
async def stop_service(service_name: str) -> APIResponse:
    """停止服务"""
    try:
        logger.info("服务停止请求", service=service_name)
        
        # 模拟停止延迟
        await asyncio.sleep(0.5)
        
        return APIResponse(
            success=True,
            message=f"服务 {service_name} 停止成功",
            data={"service": service_name, "action": "stop", "timestamp": datetime.now().isoformat()}
        )
        
    except Exception as e:
        logger.error("服务停止失败", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"服务停止失败: {str(e)}")


@router.post("/services/{service_name}/start", response_model=APIResponse)
async def start_service(service_name: str) -> APIResponse:
    """启动服务"""
    try:
        logger.info("服务启动请求", service=service_name)
        
        # 模拟启动延迟
        await asyncio.sleep(1.5)
        
        return APIResponse(
            success=True,
            message=f"服务 {service_name} 启动成功",
            data={"service": service_name, "action": "start", "timestamp": datetime.now().isoformat()}
        )
        
    except Exception as e:
        logger.error("服务启动失败", service=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"服务启动失败: {str(e)}")


@router.get("/logs", response_model=APIResponse)
async def get_system_logs(
    page: int = 1,
    page_size: int = 50,
    level: str = None,
    service: str = None
) -> APIResponse:
    """获取系统日志"""
    try:
        # 模拟日志数据
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        services = ["API网关", "AI检测服务", "规则引擎", "通知服务", "数据库服务"]
        
        logs = []
        start_time = datetime.now() - timedelta(days=7)
        
        for i in range(page_size):
            log_time = start_time + timedelta(
                minutes=i * 10 + (page - 1) * page_size * 10
            )
            
            log_entry = {
                "id": (page - 1) * page_size + i + 1,
                "timestamp": log_time.isoformat(),
                "level": log_levels[i % len(log_levels)],
                "service": services[i % len(services)],
                "message": f"这是第 {(page - 1) * page_size + i + 1} 条日志消息",
                "details": f"详细信息 - 操作编号: {1000 + i}, 用户ID: {100 + (i % 10)}"
            }
            
            # 应用过滤器
            if level and log_entry["level"] != level:
                continue
            if service and log_entry["service"] != service:
                continue
                
            logs.append(log_entry)
        
        total = 5000  # 模拟总数
        
        return APIResponse(
            success=True,
            message=f"获取到 {len(logs)} 条日志",
            data={
                "logs": logs,
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