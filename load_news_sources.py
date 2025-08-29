#!/usr/bin/env python3
"""
加载和管理新闻源配置文件的脚本
"""
import json
import requests
import time
import re
from typing import Dict, Any, List
from datetime import datetime

class NewsSourcesManager:
    """新闻源管理器"""
    
    def __init__(self, config_file: str = 'news_sources.json'):
        self.config_file = config_file
        self.news_sources = self.load_news_sources()
        self.api_base_url = 'http://localhost:9000/api/v1'
        
    def load_news_sources(self) -> Dict[str, Any]:
        """加载新闻源配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                sources = json.load(f)
            print(f"✅ 成功加载配置文件: {self.config_file}")
            return sources
        except FileNotFoundError:
            print(f"❌ 配置文件 {self.config_file} 不存在")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return {}
    
    def display_sources_summary(self):
        """显示新闻源配置摘要"""
        print("\n📋 新闻源配置摘要")
        print("=" * 60)
        
        if not self.news_sources:
            print("❌ 没有找到新闻源配置")
            return
        
        total_sources = 0
        for category, sources in self.news_sources.items():
            if isinstance(sources, list):
                count = len(sources)
                total_sources += count
                print(f"\n📁 {category.replace('_', ' ').title()}: {count} 个")
                
                for i, source in enumerate(sources[:3], 1):
                    print(f"   {i}. {source.get('name', 'N/A')} ({source.get('type', 'N/A')})")
                    print(f"      🌐 {source.get('url', 'N/A')}")
                    if source.get('notes'):
                        print(f"      📝 {source.get('notes', '')}")
                
                if count > 3:
                    print(f"      ... 还有 {count - 3} 个")
        
        print(f"\n📊 总计: {total_sources} 个新闻源")
    
    def add_sources_to_system(self, category: str = None):
        """将新闻源添加到系统中"""
        print("\n🚀 添加新闻源到系统")
        print("=" * 60)
        
        if not self.news_sources:
            print("❌ 没有找到新闻源配置")
            return
        
        sources_to_add = []
        
        if category and category in self.news_sources:
            sources_to_add = self.news_sources[category]
            print(f"📁 准备添加分类: {category.replace('_', ' ').title()}")
        else:
            for cat, sources in self.news_sources.items():
                if isinstance(sources, list):
                    sources_to_add.extend(sources)
            print("📁 准备添加所有分类的新闻源")
        
        if not sources_to_add:
            print("❌ 没有找到要添加的新闻源")
            return
        
        print(f"📊 总计: {len(sources_to_add)} 个新闻源")
        
        confirm = input("\n是否继续添加? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ 操作已取消")
            return
        
        added_sources = []
        failed_sources = []
        
        for i, source in enumerate(sources_to_add, 1):
            print(f"\n📝 处理第 {i}/{len(sources_to_add)} 个新闻源:")
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
        source_type = source.get('type', 'website')
        
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
            if source_type == 'aggregator':
                return 'generic_aggregator'
            elif source_type == 'portal':
                return 'generic_portal'
            elif source_type == 'search':
                return 'generic_search'
            else:
                return 'generic_website'
    
    def _get_crawl_interval(self, source: Dict[str, Any]) -> int:
        """根据新闻源类型获取爬取间隔"""
        source_type = source.get('type', 'website')
        
        if source_type == 'aggregator':
            return 300  # 5分钟
        elif source_type == 'portal':
            return 600  # 10分钟
        elif source_type == 'search':
            return 900  # 15分钟
        else:
            return 600  # 默认10分钟

def main():
    """主函数"""
    print("📰 新闻源配置文件管理工具")
    print("=" * 60)
    
    manager = NewsSourcesManager()
    
    if not manager.news_sources:
        print("❌ 无法加载新闻源配置，请检查配置文件")
        return
    
    while True:
        print("\n💡 请选择操作:")
        print("1. 查看配置摘要")
        print("2. 添加新闻源到系统")
        print("3. 退出")
        
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == '1':
            manager.display_sources_summary()
            
        elif choice == '2':
            print("\n📁 选择要添加的分类:")
            categories = list(manager.news_sources.keys())
            for i, cat in enumerate(categories, 1):
                print(f"   {i}. {cat.replace('_', ' ').title()}")
            print(f"   {len(categories) + 1}. 添加所有分类")
            
            cat_choice = input(f"\n请输入选择 (1-{len(categories) + 1}): ").strip()
            
            try:
                cat_index = int(cat_choice) - 1
                if 0 <= cat_index < len(categories):
                    manager.add_sources_to_system(categories[cat_index])
                elif cat_index == len(categories):
                    manager.add_sources_to_system()
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入有效数字")
            
        elif choice == '3':
            print("👋 再见！")
            break
            
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()
