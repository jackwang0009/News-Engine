@echo off
echo ========================================
echo    News Engine 启动脚本
echo ========================================
echo.

echo 正在启动Redis服务...
start "Redis" cmd /k "redis-server"

echo 等待Redis启动...
timeout /t 3 /nobreak >nul

echo 正在启动Celery Worker...
start "Celery Worker" cmd /k "python scripts/start_celery_worker.py"

echo 正在启动Celery Beat...
start "Celery Beat" cmd /k "python scripts/start_celery_beat.py"

echo 等待服务启动...
timeout /t 5 /nobreak >nul

echo 正在启动API服务...
start "API Service" cmd /k "python scripts/start_api.py"

echo.
echo ========================================
echo    所有服务已启动！
echo ========================================
echo.
echo API服务: http://localhost:9000
echo API文档: http://localhost:9000/docs
echo Flower监控: http://localhost:5555
echo.
echo 按任意键退出...
pause >nul
