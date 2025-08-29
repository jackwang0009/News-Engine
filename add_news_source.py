#!/usr/bin/env python3
"""
添加新新闻源的示例脚本
"""
import requests
import json
from datetime import datetime

def add_news_source():
    """添加新的新闻源"""
    
    # 新新闻源配置
    new_source = {
        "name": "网易新闻",
        "url": "https://news.163.com",
        "type": "website",
        "parser": "netease",
        "crawl_interval": 300  # 5分钟爬取一次
    }
    
    try:
        print("🚀 正在添加新新闻源...")
        print(f"📰 名称: {new_source['name']}")
        print(f"🌐 URL: {new_source['url']}")
        print(f"🔧 类型: {new_source['type']}")
        print(f"⚙️ 解析器: {new_source['parser']}")
        print(f"⏰ 爬取间隔: {new_source['crawl_interval']} 秒")
        print("=" * 60)
        
        # 发送POST请求创建新闻源
        response = requests.post(
            'http://localhost:9000/api/v1/sources/',
            json=new_source,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 新闻源创建成功！")
            print(f"🆔 新闻源ID: {result.get('id', 'N/A')}")
            print(f"📅 创建时间: {result.get('created_at', 'N/A')}")
            print(f"🔄 更新时间: {result.get('updated_at', 'N/A')}")
            
            return result
            
        else:
            print(f"❌ 创建失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def list_all_sources():
    """列出所有新闻源"""
    try:
        print("\n📋 当前所有新闻源:")
        print("=" * 60)
        
        response = requests.get('http://localhost:9000/api/v1/sources/')
        if response.status_code == 200:
            sources = response.json()
            
            for i, source in enumerate(sources, 1):
                print(f"\n{i}. 新闻源ID: {source.get('id', 'N/A')}")
                print(f"   名称: {source.get('name', 'N/A')}")
                print(f"   URL: {source.get('url', 'N/A')}")
                print(f"   类型: {source.get('type', 'N/A')}")
                print(f"   解析器: {source.get('parser', 'N/A')}")
                print(f"   状态: {'✅ 活跃' if source.get('is_active') else '❌ 停用'}")
                print(f"   爬取间隔: {source.get('crawl_interval', 'N/A')} 秒")
                print(f"   最后爬取: {source.get('last_crawl_time', '从未爬取')}")
                
        else:
            print(f"❌ 获取新闻源列表失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_crawler_for_source(source_id: str):
    """测试特定新闻源的爬虫"""
    try:
        print(f"\n🧪 测试新闻源 {source_id} 的爬虫...")
        print("=" * 60)
        
        # 启动爬虫任务
        task_data = {
            "source_id": source_id,
            "force_crawl": True,
            "max_pages": 3
        }
        
        response = requests.post(
            'http://localhost:9000/api/v1/crawlers/start',
            json=task_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 爬虫任务启动成功！")
            print(f"🆔 任务ID: {result.get('task', {}).get('task_id', 'N/A')}")
            print(f"📰 新闻源: {result.get('task', {}).get('source_id', 'N/A')}")
            print(f"📊 状态: {result.get('task', {}).get('status', 'N/A')}")
            print(f"⏰ 创建时间: {result.get('task', {}).get('created_at', 'N/A')}")
            
        else:
            print(f"❌ 启动爬虫任务失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def main():
    """主函数"""
    print("🆕 新闻源添加工具")
    print("=" * 60)
    
    # 1. 添加新新闻源
    new_source = add_news_source()
    
    if new_source:
        # 2. 列出所有新闻源
        list_all_sources()
        
        # 3. 测试新新闻源的爬虫
        source_id = new_source.get('id')
        if source_id:
            test_crawler_for_source(source_id)
        
        print("\n" + "=" * 60)
        print("🎉 新闻源添加完成！")
        print("\n💡 后续步骤:")
        print("1. 确保 Celery Worker 正在运行")
        print("2. 启动 Celery Beat 以启用定时爬取")
        print("3. 监控爬虫任务执行状态")
        print("4. 查看爬取到的新闻数据")
        
    else:
        print("\n❌ 新闻源添加失败，请检查:")
        print("1. API服务是否正在运行")
        print("2. 网络连接是否正常")
        print("3. 请求参数是否正确")

if __name__ == "__main__":
    main()
