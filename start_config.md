# 终端 1: 数据库服务
docker-compose up -d postgres mongodb redis elasticsearch

# 终端 2: API 服务
.venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

# 终端 3: Celery Worker
.venv\Scripts\activate
celery -A app.celery_app worker --loglevel=info

# 终端 4: Celery Beat
.venv\Scripts\activate
celery -A app.celery_app beat --loglevel=info

# 终端 5: Flower 监控
.venv\Scripts\activate
celery -A app.celery_app flower --port=5555 --host=0.0.0.0

# 查看容器运行情况
docker ps

# 测试 API 健康状态
curl http://localhost:9000/health
