#!/usr/bin/env python3
"""
启动API服务脚本
"""
import os
import sys
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings


def main():
    """启动API服务"""
    print("🚀 启动News Engine API服务...")
    print(f"📍 服务地址: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📚 API文档: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"🔧 调试模式: {'开启' if settings.DEBUG else '关闭'}")
    print(f"📝 日志级别: {settings.LOG_LEVEL}")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 API服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
