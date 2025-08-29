#!/usr/bin/env python3
"""
启动Celery Worker脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.celery_app import celery_app
from app.config import settings


def main():
    """启动Celery Worker"""
    print("🚀 启动News Engine Celery Worker...")
    print(f"🔧 队列: crawler, processor, index")
    print(f"📝 日志级别: {settings.LOG_LEVEL}")
    print(f"🌐 时区: Asia/Shanghai")
    print("-" * 50)
    
    try:
        # 启动Celery Worker
        celery_app.worker_main([
            'worker',
            '--loglevel=' + settings.LOG_LEVEL.lower(),
            '--concurrency=4',
            '--queues=crawler,processor,index,default',
            '--hostname=worker@%h',
            '--time-limit=3600',
            '--soft-time-limit=3000'
        ])
    except KeyboardInterrupt:
        print("\n👋 Celery Worker已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
