"""
API路由主文件
"""
from fastapi import APIRouter

from app.api.v1.endpoints import news, sources, crawlers, analytics, health

# 创建主路由
api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(health.router, prefix="/health", tags=["健康检查"])
api_router.include_router(news.router, prefix="/news", tags=["新闻管理"])
api_router.include_router(sources.router, prefix="/sources", tags=["新闻源管理"])
api_router.include_router(crawlers.router, prefix="/crawlers", tags=["爬虫管理"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["数据分析"])
