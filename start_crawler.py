#!/usr/bin/env python3
"""
启动爬虫系统脚本
使用配置文件中的新闻源进行爬取
"""
import json
import requests
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

class CrawlerStarter:
    """爬虫启动器"""
    
    def __init__(self):
        self.api_base_url = 'http://localhost:9000/api/v1'
        self.news_sources = self.load_news_sources()
        
    def load_news_sources(self) -> Dict[str, Any]:
        """加载新闻源配置"""
        try:
            with open('news_sources.json', 'r', encoding='utf-8') as f:
                sources = json.load(f)
            print(f"✅ 成功加载新闻源配置: {len(sources)} 个分类")
            return sources
        except FileNotFoundError:
            print("❌ 找不到 news_sources.json 配置文件")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return {}
    
    def add_news_sources(self) -> List[Dict[str, Any]]:
        """添加新闻源到系统"""
        print("\n🚀 添加新闻源到系统")
        print("=" * 60)
        
        all_sources = []
        for category, sources in self.news_sources.items():
            if isinstance(sources, list):
                all_sources.extend(sources)
        
        print(f"📊 总计: {len(all_sources)} 个新闻源")
        
        added_sources = []
        failed_sources = []
        
        for i, source in enumerate(all_sources, 1):
            print(f"\n📝 处理第 {i}/{len(all_sources)} 个新闻源:")
            print(f"   📰 名称: {source.get('name', 'N/A')}")
            print(f"   🌐 URL: {source.get('url', 'N/A')}")
            print(f"   🏷️ 类型: {source.get('type', 'N/A')}")
            
            try:
                source_data = {
                    "name": source.get('name', ''),
                    "url": source.get('url', ''),
                    "type": source.get('type', 'website'),
                    "parser": self._generate_parser_name(source),
                    "crawl_interval": self._get_crawl_interval(source),
                    "is_active": True
                }
                
                if source.get('notes'):
                    source_data['description'] = source.get('notes')
                
                response = requests.post(
                    f'{self.api_base_url}/sources/',
                    json=source_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ 添加成功! ID: {result.get('id', 'N/A')}")
                    added_sources.append({
                        'source': source,
                        'result': result
                    })
                else:
                    print(f"   ❌ 添加失败: {response.status_code}")
                    print(f"   错误详情: {response.text}")
                    failed_sources.append(source)
                    
            except Exception as e:
                print(f"   ❌ 请求失败: {str(e)}")
                failed_sources.append(source)
            
            time.sleep(1)
        
        print("\n" + "=" * 60)
        print("📊 添加结果统计:")
        print(f"✅ 成功添加: {len(added_sources)} 个")
        print(f"❌ 添加失败: {len(failed_sources)} 个")
        
        return added_sources, failed_sources
    
    def _generate_parser_name(self, source: Dict[str, Any]) -> str:
        """根据新闻源生成解析器名称"""
        name = source.get('name', '').lower()
        
        if 'baidu' in name:
            return 'baidu'
        elif 'sina' in name:
            return 'sina'
        elif 'sohu' in name:
            return 'sohu'
        elif 'qq' in name or 'tencent' in name:
            return 'tencent'
        elif 'sogou' in name:
            return 'sogou'
        elif 'toutiao' in name:
            return 'toutiao'
        elif 'yidian' in name:
            return 'yidian'
        else:
            return 'generic_website'
    
    def _get_crawl_interval(self, source: Dict[str, Any]) -> int:
        """根据新闻源类型获取爬取间隔"""
        # 根据难度分类设置不同的爬取间隔
        source_name = source.get('name', '').lower()
        
        if any(keyword in source_name for keyword in ['baidu', 'sina', 'sohu']):
            return 300  # 简单源：5分钟
        elif any(keyword in source_name for keyword in ['qq', 'tencent', 'sogou']):
            return 600  # 中等源：10分钟
        else:
            return 900  # 困难源：15分钟
    
    def start_crawler_tasks(self, sources: List[Dict[str, Any]]):
        """启动爬虫任务"""
        print("\n🕷️ 启动爬虫任务")
        print("=" * 60)
        
        if not sources:
            print("❌ 没有可用的新闻源")
            return
        
        print(f"📊 准备启动 {len(sources)} 个爬虫任务")
        
        # 逐个启动爬虫任务
        started_tasks = []
        failed_tasks = []
        
        for source in sources:
            source_id = source['result']['id']
            source_name = source['source']['name']
            
            print(f"\n📝 启动爬虫任务:")
            print(f"   📰 新闻源: {source_name}")
            print(f"   🆔 ID: {source_id}")
            
            try:
                # 启动单个爬虫任务
                response = requests.post(
                    f'{self.api_base_url}/crawlers/start',
                    json={
                        "source_id": source_id,
                        "force_crawl": False,
                        "max_pages": 5
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ 启动成功!")
                    
                    # 从响应中提取任务信息
                    task_info = result.get('task', {})
                    task_id = task_info.get('task_id', 'N/A')
                    status = task_info.get('status', 'N/A')
                    source_id = task_info.get('source_id', 'N/A')
                    created_at = task_info.get('created_at', 'N/A')
                    
                    print(f"   任务ID: {task_id}")
                    print(f"   状态: {status}")
                    print(f"   新闻源ID: {source_id}")
                    print(f"   创建时间: {created_at}")
                    
                    started_tasks.append({
                        'source_name': source_name,
                        'source_id': source_id,
                        'task_id': task_id,
                        'status': status,
                        'result': result
                    })
                else:
                    print(f"   ❌ 启动失败: {response.status_code}")
                    print(f"   错误详情: {response.text}")
                    failed_tasks.append({
                        'source_name': source_name,
                        'source_id': source_id,
                        'error': response.text
                    })
                    
            except Exception as e:
                print(f"   ❌ 启动失败: {str(e)}")
                failed_tasks.append({
                    'source_name': source_name,
                    'source_id': source_id,
                    'error': str(e)
                })
            
            time.sleep(1)
        
        print("\n" + "=" * 60)
        print("📊 爬虫任务启动结果:")
        print(f"✅ 成功启动: {len(started_tasks)} 个")
        print(f"❌ 启动失败: {len(failed_tasks)} 个")
        
        if failed_tasks:
            print("\n❌ 启动失败的新闻源:")
            for task in failed_tasks:
                print(f"   - {task['source_name']} (ID: {task['source_id']}): {task['error']}")
        
        return started_tasks, failed_tasks
    
    def check_system_status(self):
        """检查系统状态"""
        print("\n🔍 检查系统状态")
        print("=" * 60)
        
        # 检查API健康状态
        try:
            response = requests.get(f'{self.api_base_url}/health')
            if response.status_code == 200:
                health = response.json()
                print(f"✅ API服务状态: {health.get('status', 'N/A')}")
            else:
                print(f"❌ API服务异常: {response.status_code}")
        except Exception as e:
            print(f"❌ 无法连接API服务: {str(e)}")
            return False
        
        # 检查爬虫状态
        try:
            response = requests.get(f'{self.api_base_url}/crawlers/status')
            if response.status_code == 200:
                status = response.json()
                print(f"📊 爬虫系统状态: {status.get('overall_status', 'N/A')}")
                print(f"   总新闻源: {status.get('total_sources', 0)}")
                print(f"   活跃源: {status.get('active_sources', 0)}")
            else:
                print(f"❌ 无法获取爬虫状态: {response.status_code}")
        except Exception as e:
            print(f"❌ 检查爬虫状态失败: {str(e)}")
        
        return True
    
    def check_started_tasks(self, started_tasks: List[Dict[str, Any]]):
        """检查已启动任务的状态"""
        if not started_tasks:
            return
        
        print("\n🔍 检查已启动任务的状态:")
        print("=" * 60)
        
        for task in started_tasks:
            task_id = task.get('task_id')
            source_name = task.get('source_name')
            source_id = task.get('source_id')
            
            if not task_id or task_id == 'N/A':
                continue
                
            print(f"\n📝 任务状态检查:")
            print(f"   📰 新闻源: {source_name}")
            print(f"   🆔 任务ID: {task_id}")
            print(f"   📍 新闻源ID: {source_id}")
            
            try:
                # 检查任务状态
                response = requests.get(
                    f'{self.api_base_url}/crawlers/{task_id}/status',
                    timeout=10
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    print(f"   📊 状态: {status_data.get('status', 'N/A')}")
                    print(f"   📈 进度: {status_data.get('progress', 'N/A')}%")
                    print(f"   📰 已找到文章: {status_data.get('articles_found', 'N/A')}")
                    print(f"   ✅ 已处理文章: {status_data.get('articles_processed', 'N/A')}")
                else:
                    print(f"   ❌ 状态检查失败: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ 状态检查异常: {str(e)}")
            
            time.sleep(0.5)  # 避免请求过快

    def run(self):
        """运行爬虫启动器"""
        print("🕷️ 新闻爬虫系统启动器")
        print("=" * 60)
        print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查系统状态
        if not self.check_system_status():
            print("❌ 系统状态检查失败，请确保服务正常运行")
            return
        
        # 添加新闻源
        added_sources, failed_sources = self.add_news_sources()
        
        if not added_sources:
            print("❌ 没有成功添加任何新闻源，无法启动爬虫")
            return
        
        # 启动爬虫任务
        started_tasks, failed_tasks = self.start_crawler_tasks(added_sources)
        
        # 检查已启动任务的状态
        self.check_started_tasks(started_tasks)
        
        print("\n" + "=" * 60)
        print("🎉 爬虫系统启动完成！")
        print("\n💡 下一步操作:")
        print("   1. 检查 Celery Worker 是否运行: python scripts/start_celery_worker.py")
        print("   2. 检查 Celery Beat 是否运行: python scripts/start_celery_beat.py")
        print("   3. 监控爬虫状态: python check_sources.py")
        print("   4. 查看爬虫监控: http://localhost:5555")

def main():
    """主函数"""
    starter = CrawlerStarter()
    starter.run()

if __name__ == "__main__":
    main()
