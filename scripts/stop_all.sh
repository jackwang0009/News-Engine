#!/bin/bash

echo "========================================"
echo "    News Engine 停止脚本"
echo "========================================"
echo

# 停止API服务
if [ -f logs/api.pid ]; then
    API_PID=$(cat logs/api.pid)
    if kill -0 $API_PID 2>/dev/null; then
        echo "正在停止API服务 (PID: $API_PID)..."
        kill $API_PID
        sleep 2
        if kill -0 $API_PID 2>/dev/null; then
            echo "强制停止API服务..."
            kill -9 $API_PID
        fi
        echo "API服务已停止"
    else
        echo "API服务未运行"
    fi
    rm -f logs/api.pid
else
    echo "API服务未运行"
fi

# 停止Celery Beat
if [ -f logs/beat.pid ]; then
    BEAT_PID=$(cat logs/beat.pid)
    if kill -0 $BEAT_PID 2>/dev/null; then
        echo "正在停止Celery Beat (PID: $BEAT_PID)..."
        kill $BEAT_PID
        sleep 2
        if kill -0 $BEAT_PID 2>/dev/null; then
            echo "强制停止Celery Beat..."
            kill -9 $BEAT_PID
        fi
        echo "Celery Beat已停止"
    else
        echo "Celery Beat未运行"
    fi
    rm -f logs/beat.pid
else
    echo "Celery Beat未运行"
fi

# 停止Celery Worker
if [ -f logs/worker.pid ]; then
    WORKER_PID=$(cat logs/worker.pid)
    if kill -0 $WORKER_PID 2>/dev/null; then
        echo "正在停止Celery Worker (PID: $WORKER_PID)..."
        kill $WORKER_PID
        sleep 2
        if kill -0 $WORKER_PID 2>/dev/null; then
            echo "强制停止Celery Worker..."
            kill -9 $WORKER_PID
        fi
        echo "Celery Worker已停止"
    else
        echo "Celery Worker未运行"
    fi
    rm -f logs/worker.pid
else
    echo "Celery Worker未运行"
fi

# 停止Redis服务
if pgrep -x "redis-server" > /dev/null; then
    echo "正在停止Redis服务..."
    redis-cli shutdown
    sleep 2
    if pgrep -x "redis-server" > /dev/null; then
        echo "强制停止Redis服务..."
        pkill -9 redis-server
    fi
    echo "Redis服务已停止"
else
    echo "Redis服务未运行"
fi

echo
echo "========================================"
echo "    所有服务已停止！"
echo "========================================"
echo
