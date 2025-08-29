#!/usr/bin/env python3
"""
新闻爬虫系统全面健康检查脚本
"""
import requests
import json
import time
import redis
from datetime import datetime
from typing import Dict, Any, List
import socket

class SystemHealthChecker:
    """系统健康检查器"""
    
    def __init__(self):
        self.api_base_url = 'http://localhost:9000'
        self.redis_host = 'localhost'
        self.redis_port = 6379
        self.health_status = {}
        
    def check_api_health(self) -> Dict[str, Any]:
        """检查API服务健康状态"""
        print("🏥 检查API服务健康状态...")
        print("=" * 50)
        
        api_status = {
            'status': 'unknown',
            'endpoints': {},
            'response_time': 0,
            'errors': []
        }
        
        try:
            # 基础健康检查
            start_time = time.time()
            response = requests.get(f'{self.api_base_url}/health', timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                api_status['status'] = health_data.get('status', 'unknown')
                api_status['response_time'] = round(response_time * 1000, 2)  # 毫秒
                print(f"✅ 基础健康检查: {api_status['status']}")
                print(f"   ⏱️ 响应时间: {api_status['response_time']}ms")
                print(f"   📱 应用: {health_data.get('app', 'N/A')}")
                print(f"   🔢 版本: {health_data.get('version', 'N/A')}")
            else:
                api_status['status'] = 'unhealthy'
                api_status['errors'].append(f"基础健康检查失败: {response.status_code}")
                print(f"❌ 基础健康检查失败: {response.status_code}")
                
        except Exception as e:
            api_status['status'] = 'unhealthy'
            api_status['errors'].append(f"API连接失败: {str(e)}")
            print(f"❌ API连接失败: {str(e)}")
        
        # 检查详细健康状态
        try:
            response = requests.get(f'{self.api_base_url}/api/v1/health/detailed', timeout=5)
            if response.status_code == 200:
                detailed_health = response.json()
                api_status['detailed'] = detailed_health
                print(f"✅ 详细健康检查: {detailed_health.get('status', 'unknown')}")
                
                # 显示系统资源信息
                if 'system' in detailed_health:
                    system = detailed_health['system']
                    print(f"   💻 CPU使用率: {system.get('cpu_percent', 'N/A')}%")
                    print(f"   🧠 内存使用率: {system.get('memory_percent', 'N/A')}%")
                    print(f"   💾 磁盘使用率: {system.get('disk_percent', 'N/A')}%")
            else:
                print(f"⚠️ 详细健康检查失败: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ 详细健康检查异常: {str(e)}")
        
        # 检查就绪状态
        try:
            response = requests.get(f'{self.api_base_url}/api/v1/health/ready', timeout=5)
            if response.status_code == 200:
                ready_status = response.json()
                api_status['ready'] = ready_status
                print(f"✅ 就绪状态检查: {ready_status.get('status', 'unknown')}")
                
                if 'dependencies' in ready_status:
                    deps = ready_status['dependencies']
                    for dep, status in deps.items():
                        status_emoji = "✅" if status == "connected" else "❌"
                        print(f"   {status_emoji} {dep}: {status}")
            else:
                print(f"⚠️ 就绪状态检查失败: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ 就绪状态检查异常: {str(e)}")
        
        self.health_status['api'] = api_status
        return api_status
    
    def check_database_health(self) -> Dict[str, Any]:
        """检查数据库健康状态"""
        print("\n🗄️ 检查数据库健康状态...")
        print("=" * 50)
        
        db_status = {
            'status': 'unknown',
            'services': {},
            'errors': []
        }
        
        # 检查PostgreSQL
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 5432))
            sock.close()
            
            if result == 0:
                db_status['services']['postgresql'] = 'connected'
                print("✅ PostgreSQL: 连接正常")
            else:
                db_status['services']['postgresql'] = 'disconnected'
                print("❌ PostgreSQL: 连接失败")
                db_status['errors'].append("PostgreSQL连接失败")
        except Exception as e:
            db_status['services']['postgresql'] = 'error'
            print(f"❌ PostgreSQL: 检查异常 - {str(e)}")
            db_status['errors'].append(f"PostgreSQL检查异常: {str(e)}")
        
        # 检查MongoDB
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 27017))
            sock.close()
            
            if result == 0:
                db_status['services']['mongodb'] = 'connected'
                print("✅ MongoDB: 连接正常")
            else:
                db_status['services']['mongodb'] = 'disconnected'
                print("❌ MongoDB: 连接失败")
                db_status['errors'].append("MongoDB连接失败")
        except Exception as e:
            db_status['services']['mongodb'] = 'error'
            print(f"❌ MongoDB: 检查异常 - {str(e)}")
            db_status['errors'].append(f"MongoDB检查异常: {str(e)}")
        
        # 检查Redis
        try:
            r = redis.Redis(host=self.redis_host, port=self.redis_port, db=0, decode_responses=True)
            r.ping()
            db_status['services']['redis'] = 'connected'
            print("✅ Redis: 连接正常")
            
            # 获取Redis信息
            info = r.info()
            print(f"   📊 版本: {info.get('redis_version', 'Unknown')}")
            print(f"   🔗 连接数: {info.get('connected_clients', 'Unknown')}")
            print(f"   💾 内存使用: {info.get('used_memory_human', 'Unknown')}")
            
        except Exception as e:
            db_status['services']['redis'] = 'error'
            print(f"❌ Redis: 连接异常 - {str(e)}")
            db_status['errors'].append(f"Redis连接异常: {str(e)}")
        
        # 检查Elasticsearch
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 9200))
            sock.close()
            
            if result == 0:
                db_status['services']['elasticsearch'] = 'connected'
                print("✅ Elasticsearch: 连接正常")
            else:
                db_status['services']['elasticsearch'] = 'disconnected'
                print("❌ Elasticsearch: 连接失败")
                db_status['errors'].append("Elasticsearch连接失败")
        except Exception as e:
            db_status['services']['elasticsearch'] = 'error'
            print(f"❌ Elasticsearch: 检查异常 - {str(e)}")
            db_status['errors'].append(f"Elasticsearch检查异常: {str(e)}")
        
        # 确定整体状态
        connected_count = sum(1 for status in db_status['services'].values() if status == 'connected')
        total_count = len(db_status['services'])
        
        if connected_count == total_count:
            db_status['status'] = 'healthy'
        elif connected_count > 0:
            db_status['status'] = 'warning'
        else:
            db_status['status'] = 'unhealthy'
        
        print(f"\n📊 数据库状态: {db_status['status']} ({connected_count}/{total_count})")
        self.health_status['database'] = db_status
        return db_status
    
    def check_celery_health(self) -> Dict[str, Any]:
        """检查Celery健康状态"""
        print("\n🌱 检查Celery健康状态...")
        print("=" * 50)
        
        celery_status = {
            'status': 'unknown',
            'beat': 'unknown',
            'worker': 'unknown',
            'queues': {},
            'errors': []
        }
        
        try:
            # 检查Redis中的Celery状态
            r = redis.Redis(host=self.redis_host, port=self.redis_port, db=0, decode_responses=True)
            
            # 检查Beat调度器
            beat_schedule = r.get('celery:beat:schedule')
            if beat_schedule:
                celery_status['beat'] = 'running'
                print("✅ Beat调度器: 正在运行")
            else:
                celery_status['beat'] = 'stopped'
                print("❌ Beat调度器: 未运行")
                celery_status['errors'].append("Beat调度器未运行")
            
            # 检查Worker状态
            active_workers = r.smembers('celery:active')
            if active_workers:
                celery_status['worker'] = 'running'
                print(f"✅ Worker: 正在运行 ({len(active_workers)} 个)")
                for worker in active_workers:
                    print(f"   👷 {worker}")
            else:
                celery_status['worker'] = 'stopped'
                print("❌ Worker: 未运行")
                celery_status['errors'].append("Worker未运行")
            
            # 检查任务队列
            queues = ['celery', 'crawler', 'processor', 'index']
            for queue in queues:
                try:
                    queue_length = r.llen(queue)
                    celery_status['queues'][queue] = queue_length
                    if queue_length > 0:
                        print(f"📋 {queue} 队列: {queue_length} 个任务")
                    else:
                        print(f"📋 {queue} 队列: 空")
                except Exception as e:
                    celery_status['queues'][queue] = 'error'
                    print(f"❌ {queue} 队列检查失败: {str(e)}")
            
            # 检查定时任务配置
            try:
                beat_config = r.get('celery:beat:schedule')
                if beat_config:
                    print("✅ 定时任务配置: 已加载")
                else:
                    print("⚠️ 定时任务配置: 未找到")
            except Exception as e:
                print(f"⚠️ 定时任务配置检查失败: {str(e)}")
                
        except Exception as e:
            celery_status['status'] = 'error'
            celery_status['errors'].append(f"Celery检查异常: {str(e)}")
            print(f"❌ Celery检查异常: {str(e)}")
        
        # 确定整体状态
        if celery_status['beat'] == 'running' and celery_status['worker'] == 'running':
            celery_status['status'] = 'healthy'
        elif celery_status['beat'] == 'running' or celery_status['worker'] == 'running':
            celery_status['status'] = 'warning'
        else:
            celery_status['status'] = 'unhealthy'
        
        print(f"\n📊 Celery状态: {celery_status['status']}")
        self.health_status['celery'] = celery_status
        return celery_status
    
    def check_crawler_health(self) -> Dict[str, Any]:
        """检查爬虫健康状态"""
        print("\n🕷️ 检查爬虫健康状态...")
        print("=" * 50)
        
        crawler_status = {
            'status': 'unknown',
            'sources': {},
            'tasks': {},
            'errors': []
        }
        
        try:
            # 检查新闻源状态
            response = requests.get(f'{self.api_base_url}/api/v1/sources/', timeout=5)
            if response.status_code == 200:
                sources = response.json()
                crawler_status['sources']['total'] = len(sources)
                crawler_status['sources']['active'] = sum(1 for s in sources if s.get('is_active', False))
                
                print(f"📰 新闻源: {len(sources)} 个")
                print(f"✅ 活跃源: {crawler_status['sources']['active']} 个")
                
                for source in sources[:3]:  # 显示前3个
                    status_emoji = "✅" if source.get('is_active') else "❌"
                    print(f"   {status_emoji} {source.get('name', 'N/A')} ({source.get('type', 'N/A')})")
                
                if len(sources) > 3:
                    print(f"   ... 还有 {len(sources) - 3} 个新闻源")
            else:
                print(f"❌ 获取新闻源失败: {response.status_code}")
                crawler_status['errors'].append(f"获取新闻源失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 新闻源检查异常: {str(e)}")
            crawler_status['errors'].append(f"新闻源检查异常: {str(e)}")
        
        try:
            # 检查爬虫状态
            response = requests.get(f'{self.api_base_url}/api/v1/crawlers/status', timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                crawler_status['tasks'] = status_data
                
                print(f"\n📊 爬虫任务状态:")
                print(f"   🏃 运行中任务: {status_data.get('running_tasks', 0)}")
                print(f"   ⏳ 队列中任务: {status_data.get('queued_tasks', 0)}")
                print(f"   ✅ 今日完成: {status_data.get('completed_today', 0)}")
                print(f"   ❌ 今日失败: {status_data.get('failed_today', 0)}")
                print(f"   🕐 最后爬取: {status_data.get('last_crawl_time', '未知')}")
                
                overall_status = status_data.get('overall_status', 'unknown')
                status_emoji = {
                    'healthy': '✅',
                    'unhealthy': '❌',
                    'warning': '⚠️'
                }.get(overall_status, '❓')
                print(f"   🎯 整体状态: {status_emoji} {overall_status}")
                
            else:
                print(f"❌ 获取爬虫状态失败: {response.status_code}")
                crawler_status['errors'].append(f"获取爬虫状态失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 爬虫状态检查异常: {str(e)}")
            crawler_status['errors'].append(f"爬虫状态检查异常: {str(e)}")
        
        # 确定整体状态
        if crawler_status['sources'].get('active', 0) > 0:
            crawler_status['status'] = 'healthy'
        else:
            crawler_status['status'] = 'unhealthy'
        
        print(f"\n📊 爬虫状态: {crawler_status['status']}")
        self.health_status['crawler'] = crawler_status
        return crawler_status
    
    def check_news_data(self) -> Dict[str, Any]:
        """检查新闻数据状态"""
        print("\n📰 检查新闻数据状态...")
        print("=" * 50)
        
        data_status = {
            'status': 'unknown',
            'total_news': 0,
            'recent_news': 0,
            'sources_coverage': {},
            'errors': []
        }
        
        try:
            # 获取新闻列表
            response = requests.get(f'{self.api_base_url}/api/v1/news/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # 解析新闻数据
                if isinstance(data, dict):
                    if 'data' in data and isinstance(data['data'], dict):
                        news_list = data['data'].get('items', [])
                    elif 'data' in data and isinstance(data['data'], list):
                        news_list = data['data']
                    else:
                        news_list = []
                        for key, value in data.items():
                            if isinstance(value, list):
                                news_list = value
                                break
                else:
                    news_list = data
                
                data_status['total_news'] = len(news_list)
                
                if news_list:
                    print(f"✅ 总新闻数: {len(news_list)} 条")
                    
                    # 统计来源分布
                    source_count = {}
                    for news in news_list:
                        source = news.get('source_name', news.get('source', '未知'))
                        source_count[source] = source_count.get(source, 0) + 1
                    
                    print(f"📊 来源分布:")
                    for source, count in sorted(source_count.items(), key=lambda x: x[1], reverse=True):
                        print(f"   📍 {source}: {count} 条")
                    
                    # 检查最新新闻
                    recent_news = []
                    for news in news_list:
                        if news.get('publish_time'):
                            recent_news.append(news)
                    
                    data_status['recent_news'] = len(recent_news)
                    print(f"🕐 有时间戳的新闻: {len(recent_news)} 条")
                    
                    # 显示最新新闻
                    if recent_news:
                        print(f"\n📰 最新新闻:")
                        for i, news in enumerate(recent_news[:3], 1):
                            title = news.get('title', '无标题')[:50]
                            source = news.get('source_name', news.get('source', '未知'))
                            time_str = news.get('publish_time', '未知')
                            print(f"   {i}. {title}... ({source}) - {time_str}")
                    
                else:
                    print("⚠️ 暂无新闻数据")
                    data_status['status'] = 'warning'
                    
            else:
                print(f"❌ 获取新闻数据失败: {response.status_code}")
                data_status['errors'].append(f"获取新闻数据失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 新闻数据检查异常: {str(e)}")
            data_status['errors'].append(f"新闻数据检查异常: {str(e)}")
        
        # 确定整体状态
        if data_status['total_news'] > 0:
            data_status['status'] = 'healthy'
        else:
            data_status['status'] = 'warning'
        
        print(f"\n📊 新闻数据状态: {data_status['status']}")
        self.health_status['news_data'] = data_status
        return data_status
    
    def generate_health_report(self) -> Dict[str, Any]:
        """生成健康检查报告"""
        print("\n" + "=" * 60)
        print("📋 系统健康检查报告")
        print("=" * 60)
        
        # 计算整体健康状态
        component_statuses = []
        for component, status in self.health_status.items():
            if isinstance(status, dict) and 'status' in status:
                component_statuses.append(status['status'])
        
        healthy_count = sum(1 for s in component_statuses if s == 'healthy')
        warning_count = sum(1 for s in component_statuses if s == 'warning')
        unhealthy_count = sum(1 for s in component_statuses if s == 'unhealthy')
        total_count = len(component_statuses)
        
        # 确定整体状态
        if unhealthy_count == 0 and warning_count == 0:
            overall_status = 'healthy'
            overall_emoji = '✅'
        elif unhealthy_count == 0:
            overall_status = 'warning'
            overall_emoji = '⚠️'
        else:
            overall_status = 'unhealthy'
            overall_emoji = '❌'
        
        print(f"🎯 整体系统状态: {overall_emoji} {overall_status}")
        print(f"📊 组件状态统计:")
        print(f"   ✅ 健康: {healthy_count}/{total_count}")
        print(f"   ⚠️ 警告: {warning_count}/{total_count}")
        print(f"   ❌ 异常: {unhealthy_count}/{total_count}")
        
        print(f"\n🔍 详细组件状态:")
        for component, status in self.health_status.items():
            if isinstance(status, dict) and 'status' in status:
                status_emoji = {
                    'healthy': '✅',
                    'warning': '⚠️',
                    'unhealthy': '❌',
                    'unknown': '❓'
                }.get(status['status'], '❓')
                print(f"   {status_emoji} {component}: {status['status']}")
        
        # 生成建议
        print(f"\n💡 系统建议:")
        if overall_status == 'healthy':
            print("   🎉 系统运行良好，所有组件状态正常！")
        elif overall_status == 'warning':
            print("   ⚠️ 系统基本正常，但部分组件需要关注")
        else:
            print("   🚨 系统存在问题，需要立即处理")
        
        # 具体建议
        if 'celery' in self.health_status:
            celery_status = self.health_status['celery']
            if celery_status.get('beat') == 'stopped':
                print("   🔧 建议: 启动Celery Beat调度器")
            if celery_status.get('worker') == 'stopped':
                print("   🔧 建议: 启动Celery Worker")
        
        if 'database' in self.health_status:
            db_status = self.health_status['database']
            for service, status in db_status.get('services', {}).items():
                if status != 'connected':
                    print(f"   🔧 建议: 检查{service}服务状态")
        
        # 保存报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'component_statuses': self.health_status,
            'summary': {
                'healthy': healthy_count,
                'warning': warning_count,
                'unhealthy': unhealthy_count,
                'total': total_count
            }
        }
        
        try:
            with open('health_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n💾 健康检查报告已保存到: health_report.json")
        except Exception as e:
            print(f"\n⚠️ 保存报告失败: {str(e)}")
        
        return report
    
    def run_full_health_check(self):
        """运行完整健康检查"""
        print("🏥 新闻爬虫系统全面健康检查")
        print("=" * 60)
        print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 运行各项检查
        self.check_api_health()
        self.check_database_health()
        self.check_celery_health()
        self.check_crawler_health()
        self.check_news_data()
        
        # 生成报告
        report = self.generate_health_report()
        
        return report

def main():
    """主函数"""
    print("🏥 新闻爬虫系统健康检查工具")
    print("=" * 60)
    
    checker = SystemHealthChecker()
    
    print("💡 选择检查类型:")
    print("1. 完整健康检查")
    print("2. 仅检查API服务")
    print("3. 仅检查数据库")
    print("4. 仅检查Celery")
    print("5. 仅检查爬虫")
    print("6. 仅检查新闻数据")
    
    choice = input("\n请输入选择 (1-6): ").strip()
    
    if choice == '1':
        checker.run_full_health_check()
    elif choice == '2':
        checker.check_api_health()
    elif choice == '3':
        checker.check_database_health()
    elif choice == '4':
        checker.check_celery_health()
    elif choice == '5':
        checker.check_crawler_health()
    elif choice == '6':
        checker.check_news_data()
    else:
        print("❌ 无效选择，运行完整健康检查")
        checker.run_full_health_check()
    
    print("\n🎉 健康检查完成！")

if __name__ == "__main__":
    main()
