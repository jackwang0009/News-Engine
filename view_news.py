#!/usr/bin/env python3
"""
查看爬取新闻的脚本
"""
import requests
import json
from datetime import datetime

def view_all_news():
    """查看所有新闻"""
    try:
        response = requests.get('http://localhost:9000/api/v1/news/')
        if response.status_code == 200:
            data = response.json()
            
            # 处理不同的API响应结构
            if isinstance(data, dict):
                # 如果是字典格式，尝试提取新闻列表
                if 'data' in data and isinstance(data['data'], dict):
                    # 分页格式: {"data": {"items": [...], "pagination": {...}}}
                    news_list = data['data'].get('items', [])
                elif 'data' in data and isinstance(data['data'], list):
                    # 直接数据格式: {"data": [...]}
                    news_list = data['data']
                elif 'articles' in data:
                    # 文章格式: {"articles": [...]}
                    news_list = data['articles']
                else:
                    # 其他格式，尝试找到列表
                    news_list = []
                    for key, value in data.items():
                        if isinstance(value, list):
                            news_list = value
                            break
            else:
                # 直接是列表
                news_list = data
            
            if news_list:
                print(f"✅ 获取到 {len(news_list)} 条新闻")
                # 安全地显示前5条
                display_count = min(5, len(news_list))
                for i in range(display_count):
                    news = news_list[i]
                    print(f"\n{i+1}. {news.get('title', '无标题')}")
                    print(f"   来源: {news.get('source_name', news.get('source', '未知'))}")
                    print(f"   时间: {news.get('publish_time', '未知')}")
                    print(f"   分类: {news.get('category', '未知')}")
                    if news.get('summary'):
                        print(f"   摘要: {news.get('summary', '')[:100]}...")
            else:
                print("⚠️ 未找到新闻数据")
                print(f"API响应结构: {type(data)}")
                if isinstance(data, dict):
                    print(f"响应键: {list(data.keys())}")
                
        else:
            print(f"❌ 获取新闻失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        print(f"错误类型: {type(e).__name__}")

def search_news(query):
    """搜索新闻"""
    try:
        response = requests.get(f'http://localhost:9000/api/v1/news/', params={'q': query})
        if response.status_code == 200:
            data = response.json()
            
            # 处理搜索结果
            if isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], dict):
                    results = data['data'].get('items', [])
                elif 'data' in data and isinstance(data['data'], list):
                    results = data['data']
                elif 'articles' in data:
                    results = data['articles']
                else:
                    results = []
                    for key, value in data.items():
                        if isinstance(value, list):
                            results = value
                            break
            else:
                results = data
            
            if results:
                print(f"✅ 搜索 '{query}' 找到 {len(results)} 条结果")
                display_count = min(5, len(results))
                for i in range(display_count):
                    news = results[i]
                    print(f"\n{i+1}. {news.get('title', '无标题')}")
                    print(f"   来源: {news.get('source_name', news.get('source', '未知'))}")
                    print(f"   时间: {news.get('publish_time', '未知')}")
                    if news.get('summary'):
                        print(f"   摘要: {news.get('summary', '')[:100]}...")
            else:
                print(f"🔍 搜索 '{query}' 未找到结果")
                
        else:
            print(f"❌ 搜索失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 搜索请求失败: {e}")

def view_news_by_source(source_id):
    """按新闻源查看新闻"""
    try:
        response = requests.get(f'http://localhost:9000/api/v1/news/', params={'source_id': source_id})
        if response.status_code == 200:
            data = response.json()
            
            # 处理按源筛选的结果
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
            
            if news_list:
                print(f"✅ 新闻源 '{source_id}' 有 {len(news_list)} 条新闻")
                display_count = min(5, len(news_list))
                for i in range(display_count):
                    news = news_list[i]
                    print(f"\n{i+1}. {news.get('title', '无标题')}")
                    print(f"   时间: {news.get('publish_time', '未知')}")
                    if news.get('summary'):
                        print(f"   摘要: {news.get('summary', '')[:100]}...")
            else:
                print(f"🔍 新闻源 '{source_id}' 暂无新闻")
                
        else:
            print(f"❌ 获取新闻源失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def view_crawler_status():
    """查看爬虫状态"""
    try:
        response = requests.get('http://localhost:9000/api/v1/crawlers/status')
        if response.status_code == 200:
            status = response.json()
            print("📊 爬虫状态:")
            print(f"   总新闻源: {status.get('total_sources', 0)}")
            print(f"   活跃源: {status.get('active_sources', 0)}")
            print(f"   运行中任务: {status.get('running_tasks', 0)}")
            print(f"   队列中任务: {status.get('queued_tasks', 0)}")
            print(f"   今日完成: {status.get('completed_today', 0)}")
            print(f"   今日失败: {status.get('failed_today', 0)}")
            print(f"   最后爬取: {status.get('last_crawl_time', '未知')}")
            
            # 显示整体状态
            overall_status = status.get('overall_status', 'unknown')
            status_emoji = {
                'healthy': '✅',
                'unhealthy': '❌',
                'warning': '⚠️',
                'unknown': '❓'
            }.get(overall_status, '❓')
            print(f"   整体状态: {status_emoji} {overall_status}")
            
        else:
            print(f"❌ 获取爬虫状态失败: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def view_system_health():
    """查看系统健康状态"""
    try:
        response = requests.get('http://localhost:9000/health')
        if response.status_code == 200:
            health = response.json()
            print("🏥 系统健康状态:")
            print(f"   状态: {health.get('status', 'unknown')}")
            print(f"   应用: {health.get('app', 'unknown')}")
            print(f"   版本: {health.get('version', 'unknown')}")
            print(f"   时间戳: {health.get('timestamp', 'unknown')}")
        else:
            print(f"❌ 获取健康状态失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")

def main():
    """主函数"""
    print("📰 新闻查看工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 查看所有新闻")
        print("2. 搜索新闻")
        print("3. 按新闻源查看")
        print("4. 查看爬虫状态")
        print("5. 查看系统健康")
        print("6. 退出")
        
        choice = input("\n请输入选择 (1-6): ").strip()
        
        if choice == '1':
            view_all_news()
        elif choice == '2':
            query = input("请输入搜索关键词: ").strip()
            if query:
                search_news(query)
            else:
                print("❌ 关键词不能为空")
        elif choice == '3':
            source_id = input("请输入新闻源ID (如: sina_001): ").strip()
            if source_id:
                view_news_by_source(source_id)
            else:
                print("❌ 新闻源ID不能为空")
        elif choice == '4':
            view_crawler_status()
        elif choice == '5':
            view_system_health()
        elif choice == '6':
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()
