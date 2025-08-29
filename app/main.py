"""
FastAPI主应用
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import structlog

from app.config import settings
from app.api.v1.api import api_router
from app.core.logging import setup_logging

# 设置日志
setup_logging()
logger = structlog.get_logger()

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="全网新闻爬取系统API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# 请求计时中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # 记录请求日志
    logger.info(
        "HTTP Request",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
        client_ip=request.client.host if request.client else None
    )
    
    return response

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Global exception",
        exception=str(exc),
        url=str(request.url),
        method=request.method
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# 健康检查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time()
    }

# 根路径
@app.get("/")
async def root():
    return {
        "message": "Welcome to News Engine API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

# 包含API路由
app.include_router(api_router, prefix=settings.API_PREFIX)

# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("News Engine API starting up...")
    # 这里可以添加启动时的初始化代码
    # 比如数据库连接、缓存预热等

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("News Engine API shutting down...")
    # 这里可以添加关闭时的清理代码
    # 比如关闭数据库连接、清理缓存等

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
