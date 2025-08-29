@echo off
echo 🚀 News Engine 项目启动脚本
echo ================================

echo.
echo 1. 启动数据库服务...
docker-compose up -d postgres mongodb redis elasticsearch

echo.
echo 2. 等待数据库启动...
timeout /t 10 /nobreak > nul

echo.
echo 3. 检查数据库状态...
docker ps

echo.
echo 4. 启动 API 服务...
start "API Service" cmd /k "cd /d D:\repo\News_Engine && .venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload"

echo.
echo 5. 等待 API 启动...
timeout /t 5 /nobreak > nul

echo.
echo 6. 启动 Celery Worker...
start "Celery Worker" cmd /k "cd /d D:\repo\News_Engine && .venv\Scripts\activate && celery -A app.celery_app worker --loglevel=info"

echo.
echo 7. 启动 Celery Beat...
start "Celery Beat" cmd /k "cd /d D:\repo\News_Engine && .venv\Scripts\activate && celery -A app.celery_app beat --loglevel=info"

echo.
echo 8. 启动 Flower 监控...
start "Flower Monitor" cmd /k "cd /d D:\repo\News_Engine && .venv\Scripts\activate && celery -A app.celery_app flower --port=5555 --host=0.0.0.0"

echo.
echo ✅ 所有服务启动完成！
echo.
echo 🌐 可访问的服务:
echo   - API 服务: http://localhost:9000
echo   - API 文档: http://localhost:9000/docs
echo   - Flower 监控: http://localhost:5555
echo.
echo 按任意键退出...
pause > nul
