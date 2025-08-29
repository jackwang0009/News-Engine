#!/usr/bin/env python3
"""
检查Redis和Celery任务队列状态
"""
import redis
import json
from datetime import datetime

def check_redis_status():
    """检查Redis连接状态"""
    try:
        # 连接到Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # 测试连接
        r.ping()
        print("✅ Redis连接成功")
        
        # 获取Redis信息
        info = r.info()
        print(f"📊 Redis版本: {info.get('redis_version', 'Unknown')}")
        print(f"🔗 连接数: {info.get('connected_clients', 'Unknown')}")
        print(f"💾 内存使用: {info.get('used_memory_human', 'Unknown')}")
        
        return r
        
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return None

def check_celery_queues(redis_client):
    """检查Celery任务队列"""
    if not redis_client:
        return
    
    print("\n🔍 检查Celery任务队列:")
    print("=" * 50)
    
    # 检查默认队列
    try:
        default_queue = redis_client.llen('celery')
        print(f"📋 默认队列 (celery): {default_queue} 个任务")
        
        if default_queue > 0:
            # 查看队列中的任务
            tasks = redis_client.lrange('celery', 0, -1)
            print(f"   任务详情:")
            for i, task in enumerate(tasks[:3]):  # 只显示前3个
                try:
                    task_data = json.loads(task)
                    task_name = task_data.get('task', 'Unknown')
                    task_id = task_data.get('id', 'Unknown')
                    print(f"   {i+1}. {task_name} (ID: {task_id})")
                except:
                    print(f"   {i+1}. 任务数据解析失败")
            
            if default_queue > 3:
                print(f"   ... 还有 {default_queue - 3} 个任务")
    except Exception as e:
        print(f"   检查默认队列失败: {e}")
    
    # 检查爬虫队列
    try:
        crawler_queue = redis_client.llen('crawler')
        print(f"🕷️ 爬虫队列 (crawler): {crawler_queue} 个任务")
    except Exception as e:
        print(f"   检查爬虫队列失败: {e}")
    
    # 检查处理队列
    try:
        processor_queue = redis_client.llen('processor')
        print(f"⚙️ 处理队列 (processor): {processor_queue} 个任务")
    except Exception as e:
        print(f"   检查处理队列失败: {e}")
    
    # 检查索引队列
    try:
        index_queue = redis_client.llen('index')
        print(f"🔍 索引队列 (index): {index_queue} 个任务")
    except Exception as e:
        print(f"   检查索引队列失败: {e}")

def check_scheduled_tasks(redis_client):
    """检查定时任务状态"""
    if not redis_client:
        return
    
    print("\n⏰ 检查定时任务状态:")
    print("=" * 50)
    
    try:
        # 检查Beat调度器状态
        beat_schedule = redis_client.get('celery:beat:schedule')
        if beat_schedule:
            print("✅ Beat调度器正在运行")
            print("📅 定时任务已配置:")
            print("   - 爬虫任务: 每小时执行")
            print("   - 数据处理: 每30分钟执行")
            print("   - 索引更新: 每15分钟执行")
        else:
            print("⚠️ Beat调度器未运行或未配置")
            
    except Exception as e:
        print(f"   检查定时任务失败: {e}")

def check_worker_status(redis_client):
    """检查Worker状态"""
    if not redis_client:
        return
    
    print("\n👷 检查Worker状态:")
    print("=" * 50)
    
    try:
        # 检查活跃的Worker
        active_workers = redis_client.smembers('celery:active')
        if active_workers:
            print(f"✅ 活跃Worker数量: {len(active_workers)}")
            for worker in active_workers:
                print(f"   - {worker}")
        else:
            print("⚠️ 没有活跃的Worker")
            
    except Exception as e:
        print(f"   检查Worker状态失败: {e}")

def main():
    """主函数"""
    print("🔍 Redis和Celery状态检查")
    print("=" * 60)
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查Redis连接
    redis_client = check_redis_status()
    
    if redis_client:
        # 检查各种队列和状态
        check_celery_queues(redis_client)
        check_scheduled_tasks(redis_client)
        check_worker_status(redis_client)
        
        print("\n" + "=" * 60)
        print("📋 检查完成！")
        
        # 提供建议
        print("\n💡 建议:")
        if redis_client.llen('celery') == 0:
            print("   - 当前没有待执行的任务")
            print("   - 请确保已启动 Celery Beat 和 Worker")
        else:
            print("   - 有任务在队列中等待执行")
            print("   - 请确保 Worker 正在运行")
    else:
        print("\n❌ 无法连接到Redis，请检查:")
        print("   1. Docker容器是否启动: docker ps")
        print("   2. Redis服务是否正常: docker logs news_engine_redis")

if __name__ == "__main__":
    main()
