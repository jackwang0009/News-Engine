#!/usr/bin/env python3
"""
查看新闻源信息的脚本
"""
import requests
import json
from datetime import datetime

def check_sources():
    """查看所有新闻源"""
    try:
        response = requests.get('http://localhost:9000/api/v1/sources/')
        if response.status_code == 200:
            sources = response.json()
            print(f"📰 找到 {len(sources)} 个新闻源:")
            print("=" * 60)
            
            for i, source in enumerate(sources, 1):
                print(f"\n{i}. 新闻源ID: {source.get('id', 'N/A')}")
                print(f"   名称: {source.get('name', 'N/A')}")
                print(f"   URL: {source.get('url', 'N/A')}")
                print(f"   类型: {source.get('type', 'N/A')}")
                print(f"   解析器: {source.get('parser', 'N/A')}")
                print(f"   状态: {'✅ 活跃' if source.get('is_active') else '❌ 停用'}")
                print(f"   爬取间隔: {source.get('crawl_interval', 'N/A')} 秒")
                print(f"   最后爬取: {source.get('last_crawl_time', '从未爬取')}")
                print(f"   创建时间: {source.get('created_at', 'N/A')}")
                
        else:
            print(f"❌ 获取新闻源失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def check_crawler_status():
    """查看爬虫状态"""
    try:
        response = requests.get('http://localhost:9000/api/v1/crawlers/status')
        if response.status_code == 200:
            status = response.json()
            print("\n📊 爬虫状态:")
            print("=" * 60)
            print(f"总新闻源数量: {status.get('total_sources', 0)}")
            print(f"活跃新闻源: {status.get('active_sources', 0)}")
            print(f"运行中任务: {status.get('running_tasks', 0)}")
            print(f"队列中任务: {status.get('queued_tasks', 0)}")
            print(f"今日完成: {status.get('completed_today', 0)} 条")
            print(f"今日失败: {status.get('failed_today', 0)} 条")
            print(f"最后爬取时间: {status.get('last_crawl_time', '未知')}")
            print(f"整体状态: {status.get('overall_status', '未知')}")
        else:
            print(f"❌ 获取爬虫状态失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def check_recent_news():
    """查看最近的新闻数据"""
    try:
        response = requests.get('http://localhost:9000/api/v1/news/')
        if response.status_code == 200:
            news_data = response.json()
            print(f"\n📰 最近新闻数据:")
            print("=" * 80)
            print(f"📊 总新闻数量: {len(news_data) if isinstance(news_data, list) else '非列表'}")
            
            # 处理不同的响应格式
            if isinstance(news_data, dict):
                print(f"🔍 新闻响应字段: {list(news_data.keys())}")
                if 'data' in news_data and 'items' in news_data['data']:
                    news_list = news_data['data']['items']
                elif 'articles' in news_data:
                    news_list = news_data['articles']
                else:
                    news_list = []
            else:
                news_list = news_data if isinstance(news_data, list) else []
            
            if news_list:
                # 显示最新的几条新闻
                recent_news = news_list[:3]
                for i, news in enumerate(recent_news, 1):
                    print(f"\n{i}. 📰 {news.get('title', '无标题')}")
                    print(f"    📍 来源: {news.get('source', '未知')}")
                    print(f"    🌐 URL: {news.get('url', '无链接')}")
                    print(f"    📅 发布时间: {news.get('published_at', '未知')}")
                    print(f"    📝 摘要: {news.get('summary', '无摘要')[:100] if news.get('summary') else '无摘要'}...")
            else:
                print("    📭 暂无新闻数据")
                
        else:
            print(f"❌ 获取新闻数据失败: {response.status_code}")
            print(f"错误详情: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()

def test_api_directly():
    """直接测试API，显示原始响应"""
    print("\n🧪 直接测试API响应:")
    print("=" * 80)
    
    # 测试新闻源API
    print("📡 测试 /api/v1/sources/ 接口:")
    try:
        response = requests.get('http://localhost:9000/api/v1/sources/')
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text[:500]}...")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试爬虫状态API
    print("\n📡 测试 /api/v1/crawlers/status 接口:")
    try:
        response = requests.get('http://localhost:9000/api/v1/crawlers/status')
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}...")
    except Exception as e:
        print(f"请求失败: {e}")

def main():
    """主函数"""
    print("🔍 新闻源信息查看工具")
    print("=" * 80)
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 直接测试API
    test_api_directly()
    
    # 查看爬虫状态
    check_crawler_status()
    
    # 查看新闻源详情
    check_sources()
    
    # 查看最近的新闻数据
    check_recent_news()
    
    print("\n" + "=" * 80)
    print("🎉 检查完成！")
    print("\n💡 提示:")
    print("   - 新添加的新闻源会显示 🆕 标记")
    print("   - 新闻源按创建时间排序，最新的在前面")
    print("   - 可以运行 'python load_news_sources.py' 添加更多新闻源")

if __name__ == "__main__":
    main()
