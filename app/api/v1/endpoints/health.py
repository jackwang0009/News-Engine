"""
健康检查端点
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import time
import psutil
import socket

from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


def check_postgresql() -> bool:
    """检查PostgreSQL连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 5432))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_mongodb() -> bool:
    """检查MongoDB连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 27017))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_redis() -> bool:
    """检查Redis连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 6379))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_elasticsearch() -> bool:
    """检查Elasticsearch连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 9200))
        sock.close()
        return result == 0
    except Exception:
        return False


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """基本健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "News Engine API"
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """详细健康检查"""
    try:
        # 系统资源信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 进程信息
        process = psutil.Process()
        process_memory = process.memory_info()
        
        health_info = {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "News Engine API",
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
                "disk_total": disk.total
            },
            "process": {
                "pid": process.pid,
                "memory_rss": process_memory.rss,
                "memory_vms": process_memory.vms,
                "cpu_percent": process.cpu_percent(),
                "create_time": process.create_time()
            }
        }
        
        logger.info("Detailed health check completed", health_status="healthy")
        return health_info
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e)
        }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """就绪状态检查"""
    try:
        # 执行真实的依赖检查
        postgres_status = check_postgresql()
        mongodb_status = check_mongodb()
        redis_status = check_redis()
        elasticsearch_status = check_elasticsearch()
        
        # 所有依赖都可用才算就绪
        all_ready = all([postgres_status, mongodb_status, redis_status, elasticsearch_status])
        
        dependencies = {
            "postgresql": "connected" if postgres_status else "disconnected",
            "mongodb": "connected" if mongodb_status else "disconnected",
            "redis": "connected" if redis_status else "disconnected",
            "elasticsearch": "connected" if elasticsearch_status else "disconnected"
        }
        
        return {
            "status": "ready" if all_ready else "not_ready",
            "timestamp": time.time(),
            "dependencies": dependencies,
            "overall_status": "healthy" if all_ready else "unhealthy"
        }
        
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return {
            "status": "not_ready",
            "timestamp": time.time(),
            "error": str(e)
        }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """存活状态检查"""
    return {
        "status": "alive",
        "timestamp": time.time(),
        "service": "News Engine API"
    }
