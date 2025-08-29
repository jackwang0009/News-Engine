"""
Celery应用配置
"""
from celery import Celery
from app.config import settings

# 创建Celery实例
celery_app = Celery(
    "news_engine",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.crawler_tasks",
        "app.tasks.processor_tasks",
        "app.tasks.index_tasks"
    ]
)

# Celery配置
celery_app.conf.update(
    # 任务序列化格式
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区设置
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务路由
    task_routes={
        "app.tasks.crawler_tasks.*": {"queue": "crawler"},
        "app.tasks.processor_tasks.*": {"queue": "processor"},
        "app.tasks.index_tasks.*": {"queue": "index"},
    },
    
    # 队列配置
    task_default_queue="default",
    task_queues={
        "default": {"exchange": "default", "routing_key": "default"},
        "crawler": {"exchange": "crawler", "routing_key": "crawler"},
        "processor": {"exchange": "processor", "routing_key": "processor"},
        "index": {"exchange": "index", "routing_key": "index"},
    },
    
    # 任务执行配置
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    
    # 重试配置
    task_compression="gzip",
    result_compression="gzip",
    
    # 监控配置
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # 日志配置
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",

    # Windows兼容性配置
    worker_pool_restarts=True,
    worker_pool='solo',  # Windows上使用solo池
    worker_concurrency=1,
    
    # 禁用fork (Windows不支持)
    worker_disable_rate_limits=True,
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    "crawl-news-every-hour": {
        "task": "crawler.schedule_crawler_task",
        "schedule": 3600.0,  # 每小时执行一次
        "args": (),
    },
    "process-news-every-30min": {
        "task": "processor.schedule_processor_task",
        "schedule": 1800.0,  # 每30分钟执行一次
        "args": (),
    },
    "index-news-every-15min": {
        "task": "index.schedule_index_task",
        "schedule": 900.0,  # 每15分钟执行一次
        "args": (),
    },
}

if __name__ == "__main__":
    celery_app.start()
