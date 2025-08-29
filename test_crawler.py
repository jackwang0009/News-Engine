#!/usr/bin/env python3
"""
测试爬虫系统
"""
import requests
import json
import time

def test_api_health():
    """测试 API 健康状态"""
    try:
        response = requests.get('http://localhost:9000/health')
        print(f"✅ API 健康检查: {response.status_code}")
        print(f"响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API 健康检查失败: {e}")
        return False

def test_crawler_api():
    """测试爬虫 API"""
    try:
        # 测试获取爬虫状态
        response = requests.get('http://localhost:9000/api/v1/crawlers/status')
        print(f"✅ 爬虫状态 API: {response.status_code}")
        print(f"响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 爬虫 API 测试失败: {e}")
        return False

def test_flower_monitor():
    """测试 Flower 监控"""
    try:
        response = requests.get('http://localhost:5555/')
        print(f"✅ Flower 监控: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Flower 监控测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🕷️ 爬虫系统测试开始...")
    print("=" * 50)
    
    # 测试 API 健康状态
    api_ok = test_api_health()
    
    # 测试爬虫 API
    crawler_ok = test_crawler_api()
    
    # 测试 Flower 监控
    flower_ok = test_flower_monitor()
    
    print("=" * 50)
    print("📊 测试结果总结:")
    print(f"API 服务: {'✅ 正常' if api_ok else '❌ 异常'}")
    print(f"爬虫 API: {'✅ 正常' if crawler_ok else '❌ 异常'}")
    print(f"Flower 监控: {'✅ 正常' if flower_ok else '❌ 异常'}")
    
    if api_ok and crawler_ok and flower_ok:
        print("\n🎉 爬虫系统启动成功！")
        print("\n🌐 可访问的服务:")
        print("- API 服务: http://localhost:9000")
        print("- API 文档: http://localhost:9000/docs")
        print("- Flower 监控: http://localhost:5555")
        print("- 健康检查: http://localhost:9000/health")
    else:
        print("\n⚠️ 部分服务启动异常，请检查日志")

if __name__ == "__main__":
    main()
