"""
爬虫管理端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.schemas.requests import CrawlerTaskRequest
from app.core.logging import get_logger
from app.celery_app import celery_app
from app.tasks.crawler_tasks import start_crawler_task as celery_start_crawler_task

router = APIRouter()
logger = get_logger(__name__)

# In-memory task registry on the router instance
if not hasattr(router, "_tasks"):
    router._tasks = {}


@router.get("/status")
async def get_crawler_status():
    """获取爬虫状态概览"""
    try:
        # TODO: 实现实际的状态获取逻辑
        # 从数据库和Celery获取真实的爬虫状态
        
        logger.info("Get crawler status")
        
        # TODO: 从数据库获取真实爬虫状态数据
        # status = await crawler_service.get_status_overview()
        
        # 临时返回空结果，等待真实数据
        status = {
            "total_sources": 0,
            "active_sources": 0,
            "running_tasks": 0,
            "queued_tasks": 0,
            "completed_today": 0,
            "failed_today": 0,
            "last_crawl_time": None,
            "overall_status": "unknown"
        }
        
        return status
        
    except Exception as e:
        logger.error("Get crawler status failed", error=str(e))
        raise HTTPException(status_code=500, detail="获取爬虫状态失败")


@router.get("/tasks")
async def list_crawler_tasks(
    status: Optional[str] = Query(None, description="任务状态"),
    source_id: Optional[str] = Query(None, description="新闻源ID"),
    limit: int = Query(50, ge=1, le=200, description="数量限制")
):
    """获取爬虫任务列表"""
    try:
        logger.info("List crawler tasks", status=status, source_id=source_id, limit=limit)
        tasks = list(getattr(router, "_tasks", {}).values())
        
        # 过滤
        if status:
            tasks = [t for t in tasks if str(t.get("status")) == status]
        if source_id:
            tasks = [t for t in tasks if str(t.get("source_id")) == source_id]
        
        # 限制数量
        tasks = tasks[:limit]
        
        return {
            "tasks": tasks,
            "total": len(tasks),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error("List crawler tasks failed", error=str(e))
        raise HTTPException(status_code=500, detail="获取任务列表失败")


@router.post("/start")
async def start_crawler_task(request: CrawlerTaskRequest):
    """启动爬虫任务"""
    try:
        # 触发 Celery 任务（发送到 crawler 队列）
        # 使用 apply_async 以便显式选择队列
        celery_result = celery_start_crawler_task.apply_async(
            args=[request.source_id],
            kwargs={},
            queue="crawler"
        )
        real_task_id = celery_result.id

        logger.info(
            "Start crawler task",
            source_id=request.source_id,
            force_crawl=request.force_crawl,
            max_pages=request.max_pages
        )
        
        # 登记任务到内存注册表（用真实 Celery task_id）
        task_id = real_task_id
        task_info = {
            "task_id": task_id,
            "source_id": request.source_id,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat(),
            "estimated_start": datetime.utcnow().isoformat(),
            "force_crawl": request.force_crawl,
            "max_pages": request.max_pages,
            # 以下字段用于状态查询展示
            "progress": 0,
            "articles_found": 0,
            "articles_processed": 0
        }
        router._tasks[task_id] = task_info
        
        return {
            "status": "success",
            "message": "爬虫任务已启动",
            "task": task_info,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error("Start crawler task failed", error=str(e))
        raise HTTPException(status_code=500, detail="启动爬虫任务失败")


@router.post("/{task_id}/stop")
async def stop_crawler_task(task_id: str):
    """停止爬虫任务"""
    try:
        # TODO: 实现实际的任务停止逻辑
        
        logger.info("Stop crawler task", task_id=task_id)
        
        return {
            "status": "success",
            "message": f"爬虫任务 {task_id} 已停止",
            "task_id": task_id,
            "stopped_at": datetime.utcnow().isoformat(),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error("Stop crawler task failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="停止爬虫任务失败")


@router.get("/{task_id}/status")
async def get_task_status(task_id: str):
    """获取任务状态详情"""
    try:
        # 读取内存中的任务注册表
        task = getattr(router, "_tasks", {}).get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 临时：返回当前登记的任务信息
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get task status failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="获取任务状态失败")


@router.post("/batch/start")
async def start_batch_crawler_tasks(
    source_ids: List[str],
    force_crawl: bool = False
):
    """批量启动爬虫任务"""
    try:
        # TODO: 实现实际的批量任务启动逻辑
        # 批量启动真实的Celery爬虫任务
        
        logger.info("Start batch crawler tasks", source_count=len(source_ids), force_crawl=force_crawl)
        
        # TODO: 批量启动真实爬虫任务
        # tasks = await crawler_service.start_batch_tasks(source_ids, force_crawl)
        
        return {
            "status": "success",
            "message": "批量启动功能待实现",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error("Start batch crawler tasks failed", error=str(e))
        raise HTTPException(status_code=500, detail="批量启动爬虫任务失败")


@router.get("/statistics")
async def get_crawler_statistics(
    days: int = Query(7, ge=1, le=30, description="统计天数")
):
    """获取爬虫统计信息"""
    try:
        # TODO: 实现实际的统计信息获取逻辑
        # 从数据库获取真实的爬虫统计信息
        
        logger.info("Get crawler statistics", days=days)
        
        # TODO: 从数据库获取真实统计信息
        # statistics = await crawler_service.get_statistics(days)
        
        # 临时返回空结果，等待真实数据
        statistics = {
            "period_days": days,
            "total_articles": 0,
            "total_sources": 0,
            "success_rate": 0.0,
            "average_response_time": 0.0,
            "daily_stats": [],
            "source_performance": [],
            "timestamp": datetime.utcnow()
        }
        
        return statistics
        
    except Exception as e:
        logger.error("Get crawler statistics failed", error=str(e))
        raise HTTPException(status_code=500, detail="获取爬虫统计信息失败")
