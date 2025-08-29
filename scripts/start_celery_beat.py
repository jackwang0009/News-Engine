#!/usr/bin/env python3
"""
启动Celery Beat脚本
"""
import os
import sys
from pathlib import Path
import tempfile

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.celery_app import celery_app
from app.config import settings


def main():
    """启动Celery Beat"""
    print("🚀 启动News Engine Celery Beat...")
    print(f"⏰ 定时任务:")
    print(f"   - 爬虫任务: 每小时执行")
    print(f"   - 处理任务: 每30分钟执行")
    print(f"   - 索引任务: 每15分钟执行")
    print(f"📝 日志级别: {settings.LOG_LEVEL}")
    print(f"🌐 时区: Asia/Shanghai")
    print("-" * 50)
    
    try:
        # 兼容Windows：确保调度与PID目录存在
        tmp_dir_env = os.environ.get("CELERY_TMP_DIR")
        if tmp_dir_env:
            tmp_dir = Path(tmp_dir_env)
        else:
            # 使用系统临时目录下的news_engine子目录
            tmp_dir = Path(tempfile.gettempdir()) / "news_engine"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        schedule_file = str(tmp_dir / "celerybeat-schedule")
        pid_file = str(tmp_dir / "celerybeat.pid")

        # 启动Celery Beat
        celery_app.start([
            'beat',
            '--loglevel=' + settings.LOG_LEVEL.lower(),
            '--scheduler=celery.beat:PersistentScheduler',
            f'--schedule={schedule_file}',
            f'--pidfile={pid_file}'
        ])
    except KeyboardInterrupt:
        print("\n👋 Celery Beat已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
