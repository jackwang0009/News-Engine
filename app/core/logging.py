"""
日志配置模块
"""
import sys
import logging
from typing import Any, Dict
import structlog
from structlog.stdlib import LoggerFactory

from app.config import settings


def setup_logging() -> None:
    """设置日志配置"""
    
    # 配置标准库日志
    logging.basicConfig(
        format=settings.LOG_FORMAT,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        stream=sys.stdout
    )
    
    # 配置structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """获取日志记录器"""
    return structlog.get_logger(name)


class LoggerMixin:
    """日志记录器混入类"""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs: Any) -> None:
        """记录信息日志"""
        self.logger.info(message, **kwargs)
    
    def log_error(self, message: str, **kwargs: Any) -> None:
        """记录错误日志"""
        self.logger.error(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs: Any) -> None:
        """记录警告日志"""
        self.logger.warning(message, **kwargs)
    
    def log_debug(self, message: str, **kwargs: Any) -> None:
        """记录调试日志"""
        self.logger.debug(message, **kwargs)


def log_function_call(func_name: str, **kwargs: Any) -> None:
    """记录函数调用日志"""
    logger = get_logger("function_call")
    logger.info(f"Function {func_name} called", **kwargs)


def log_crawler_status(source: str, status: str, **kwargs: Any) -> None:
    """记录爬虫状态日志"""
    logger = get_logger("crawler_status")
    logger.info(f"Crawler {source} status: {status}", source=source, status=status, **kwargs)


def log_task_status(task_id: str, task_name: str, status: str, **kwargs: Any) -> None:
    """记录任务状态日志"""
    logger = get_logger("task_status")
    logger.info(
        f"Task {task_name} ({task_id}) status: {status}",
        task_id=task_id,
        task_name=task_name,
        status=status,
        **kwargs
    )
