#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能监控预警系统 - FastAPI主应用入口
专家级微服务架构，支持高并发和高性能
"""

import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.core.database import init_db, close_db
from app.models.schemas import APIResponse


# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# 应用启动时间
APP_START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    startup_start = time.time()
    logger.info("🚀 智能监控预警系统启动中...", version=settings.APP_VERSION)
    
    try:
        # 初始化数据库
        await init_db()
        logger.info("✅ 数据库初始化完成")
        
        # 初始化其他服务
        # TODO: 初始化Redis、AI服务等
        
        startup_time = time.time() - startup_start
        logger.info("🎉 系统启动完成", startup_time_seconds=f"{startup_time:.2f}")
        
    except Exception as e:
        logger.error("❌ 系统启动失败", error=str(e), exc_info=True)
        raise
    
    yield  # 应用运行期间
    
    # 应用关闭清理
    logger.info("🔄 系统关闭清理中...")
    try:
        await close_db()
        logger.info("✅ 数据库连接已关闭")
    except Exception as e:
        logger.error("❌ 清理过程出错", error=str(e), exc_info=True)
    
    logger.info("👋 智能监控预警系统已关闭")


def create_application() -> FastAPI:
    """创建FastAPI应用实例"""
    
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/api/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
        debug=settings.DEBUG,
    )
    
    # 添加中间件
    setup_middleware(app)
    
    # 设置路由
    setup_routes(app)
    
    # 设置异常处理
    setup_exception_handlers(app)
    
    # 设置监控
    setup_monitoring(app)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """设置中间件"""
    
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # 受信任主机中间件（生产环境）
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*"]  # 在生产中应该配置具体域名
        )
    
    # Gzip压缩中间件
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000
    )
    
    # 请求处理时间中间件
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(f"{process_time:.4f}")
        
        # 记录慢请求
        if process_time > 1.0:
            logger.warning(
                "慢请求检测",
                method=request.method,
                url=str(request.url),
                process_time=f"{process_time:.4f}s"
            )
        
        return response


def setup_routes(app: FastAPI) -> None:
    """设置路由"""
    
    # 健康检查端点
    @app.get("/health", response_model=APIResponse, tags=["系统"])
    async def health_check():
        """系统健康检查"""
        uptime = time.time() - APP_START_TIME
        return APIResponse(
            success=True,
            message="系统运行正常",
            data={
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "uptime_seconds": round(uptime, 2),
                "uptime_human": f"{uptime // 3600:.0f}h {(uptime % 3600) // 60:.0f}m {uptime % 60:.1f}s"
            }
        )
    
    # 根路径重定向
    @app.get("/", tags=["系统"])
    async def root():
        """根路径信息"""
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/api/docs" if settings.DEBUG else "文档在生产环境中已禁用",
            "health": "/health",
        }
    
    # TODO: 添加API路由
    from app.api.v1.api import api_router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)


def setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP异常处理"""
        logger.warning(
            "HTTP异常",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
            method=request.method
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=APIResponse(
                success=False,
                message=exc.detail,
                data={"status_code": exc.status_code}
            ).dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理"""
        logger.error(
            "未处理异常",
            error=str(exc),
            path=request.url.path,
            method=request.method,
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content=APIResponse(
                success=False,
                message="服务器内部错误" if settings.is_production else str(exc),
                data={"error_type": type(exc).__name__}
            ).dict()
        )


def setup_monitoring(app: FastAPI) -> None:
    """设置监控"""
    if settings.ENABLE_METRICS:
        # Prometheus监控
        instrumentator = Instrumentator(
            should_group_status_codes=False,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/metrics", "/health"],
            env_var_name="ENABLE_METRICS",
            inprogress_name="inprogress",
            inprogress_labels=True,
        )
        
        instrumentator.instrument(app)
        instrumentator.expose(app, endpoint="/metrics", tags=["监控"])
        
        logger.info("✅ Prometheus监控已启用", endpoint="/metrics")


# 创建应用实例
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🌟 开发模式启动", host=settings.HOST, port=settings.PORT)
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG,
    )