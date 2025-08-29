#!/bin/bash

echo "========================================"
echo "    News Engine 启动脚本"
echo "========================================"
echo

# 检查Redis是否运行
if ! pgrep -x "redis-server" > /dev/null; then
    echo "正在启动Redis服务..."
    redis-server --daemonize yes
    sleep 3
else
    echo "Redis服务已在运行"
fi

# 启动Celery Worker
echo "正在启动Celery Worker..."
nohup python scripts/start_celery_worker.py > logs/worker.log 2>&1 &
WORKER_PID=$!
echo "Celery Worker已启动 (PID: $WORKER_PID)"

# 启动Celery Beat
echo "正在启动Celery Beat..."
nohup python scripts/start_celery_beat.py > logs/beat.log 2>&1 &
BEAT_PID=$!
echo "Celery Beat已启动 (PID: $BEAT_PID)"

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 启动API服务
echo "正在启动API服务..."
nohup python scripts/start_api.py > logs/api.log 2>&1 &
API_PID=$!
echo "API服务已启动 (PID: $API_PID)"

echo
echo "========================================"
echo "    所有服务已启动！"
echo "========================================"
echo
echo "API服务: http://localhost:9000"
echo "API文档: http://localhost:9000/docs"
echo "Flower监控: http://localhost:5555"
echo
echo "进程ID:"
echo "  Worker: $WORKER_PID"
echo "  Beat:   $BEAT_PID"
echo "  API:    $API_PID"
echo
echo "日志文件:"
echo "  Worker: logs/worker.log"
echo "  Beat:   logs/beat.log"
echo "  API:    logs/api.log"
echo
echo "按Ctrl+C停止所有服务"

# 保存PID到文件
echo $WORKER_PID > logs/worker.pid
echo $BEAT_PID > logs/beat.pid
echo $API_PID > logs/api.pid

# 等待用户中断
trap 'echo "正在停止所有服务..."; kill $WORKER_PID $BEAT_PID $API_PID 2>/dev/null; rm -f logs/*.pid; echo "所有服务已停止"; exit 0' INT

# 保持脚本运行
while true; do
    sleep 1
done
