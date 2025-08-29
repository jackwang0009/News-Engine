#!/usr/bin/env python3
"""
智能新闻源发现和配置工具
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
from typing import List, Dict, Any, Optional
import time

class SmartSourceDiscovery:
    """智能新闻源发现器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def discover_news_sources(self, seed_url: str) -> List[Dict[str, Any]]:
        """智能发现新闻源"""
        print(f"🔍 正在分析网站: {seed_url}")
        print("=" * 60)
        
        discovered_sources = []
        
        try:
            # 1. 获取主页内容
            response = self.session.get(seed_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 2. 自动识别网站类型
            site_type = self.identify_site_type(soup, seed_url)
            print(f"🏷️ 识别网站类型: {site_type}")
            
            # 3. 查找RSS源
            rss_sources = self.find_rss_feeds(soup, seed_url)
            if rss_sources:
                discovered_sources.extend(rss_sources)
                print(f"📡 发现 {len(rss_sources)} 个RSS源")
            
            # 4. 分析网站结构
            if site_type == "news_site":
                website_sources = self.analyze_news_structure(soup, seed_url)
                if website_sources:
                    discovered_sources.extend(website_sources)
                    print(f"🌐 发现 {len(website_sources)} 个网站爬虫源")
            
            # 5. 智能生成配置
            for source in discovered_sources:
                source['config'] = self.generate_crawler_config(source)
            
            return discovered_sources
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            return []
    
    def identify_site_type(self, soup: BeautifulSoup, url: str) -> str:
        """识别网站类型"""
        # 检查是否包含新闻特征
        news_indicators = [
            'news', '新闻', '资讯', '报道', '头条',
            'article', 'story', 'post', 'blog'
        ]
        
        text_content = soup.get_text().lower()
        title = soup.title.get_text().lower() if soup.title else ""
        
        # 检查页面结构
        has_news_structure = any([
            soup.select('.news-list'),
            soup.select('.article-list'),
            soup.select('.post-list'),
            soup.select('[class*="news"]'),
            soup.select('[class*="article"]')
        ])
        
        if any(indicator in text_content for indicator in news_indicators) or has_news_structure:
            return "news_site"
        elif "rss" in text_content or "feed" in text_content:
            return "rss_site"
        else:
            return "general_site"
    
    def find_rss_feeds(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """查找RSS订阅源"""
        rss_sources = []
        
        # 1. 查找RSS链接标签
        rss_links = soup.find_all('link', {
            'type': ['application/rss+xml', 'application/atom+xml', 'text/xml']
        })
        
        for link in rss_links:
            href = link.get('href')
            if href:
                rss_url = urljoin(base_url, href)
                title = link.get('title', 'RSS订阅')
                
                rss_sources.append({
                    'name': f"{title} - RSS",
                    'url': rss_url,
                    'type': 'rss',
                    'parser': 'rss',
                    'crawl_interval': 600,  # 10分钟
                    'discovery_method': 'rss_link_tag'
                })
        
        # 2. 检查常见RSS路径
        common_rss_paths = [
            '/rss.xml', '/feed.xml', '/atom.xml',
            '/news/rss', '/feed', '/rss',
            '/sitemap.xml', '/sitemap_news.xml'
        ]
        
        for path in common_rss_paths:
            try:
                rss_url = urljoin(base_url, path)
                response = self.session.head(rss_url, timeout=5)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'xml' in content_type or 'rss' in content_type:
                        rss_sources.append({
                            'name': f"RSS源 - {path}",
                            'url': rss_url,
                            'type': 'rss',
                            'parser': 'rss',
                            'crawl_interval': 600,
                            'discovery_method': 'common_path'
                        })
            except:
                continue
        
        return rss_sources
    
    def analyze_news_structure(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """分析新闻网站结构"""
        website_sources = []
        
        # 1. 查找新闻列表页
        news_list_patterns = [
            'news', '资讯', '报道', '头条', '要闻',
            'article', 'story', 'post', 'blog'
        ]
        
        # 查找导航链接
        nav_links = soup.find_all('a', href=True)
        news_sections = []
        
        for link in nav_links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            
            # 检查是否是新闻相关链接
            if any(pattern in text for pattern in news_list_patterns):
                news_url = urljoin(base_url, href)
                news_sections.append({
                    'name': link.get_text(strip=True),
                    'url': news_url,
                    'text': text
                })
        
        # 2. 生成网站爬虫配置
        if news_sections:
            # 选择主要的新闻版块
            main_news_section = max(news_sections, 
                                  key=lambda x: len([p for p in news_list_patterns if p in x['text']]))
            
            website_sources.append({
                'name': f"{main_news_section['name']} - 网站爬虫",
                'url': main_news_section['url'],
                'type': 'website',
                'parser': 'auto_generated',
                'crawl_interval': 300,  # 5分钟
                'discovery_method': 'structure_analysis',
                'section_name': main_news_section['name']
            })
        
        return website_sources
    
    def generate_crawler_config(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """智能生成爬虫配置"""
        config = {
            'basic': {
                'delay': 1.0,
                'timeout': 30,
                'max_retries': 3,
                'max_pages': 10
            }
        }
        
        if source['type'] == 'rss':
            config['rss'] = {
                'parse_items': True,
                'parse_content': True,
                'max_items': 50
            }
        elif source['type'] == 'website':
            config['website'] = {
                'list_page_selectors': self.suggest_selectors(source['url']),
                'article_selectors': self.suggest_article_selectors(),
                'pagination_selectors': self.suggest_pagination_selectors()
            }
        
        return config
    
    def suggest_selectors(self, url: str) -> Dict[str, str]:
        """建议CSS选择器"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 智能识别选择器
            selectors = {}
            
            # 查找文章列表容器
            list_containers = soup.select('[class*="list"], [class*="news"], [class*="article"]')
            if list_containers:
                selectors['container'] = self.generate_css_selector(list_containers[0])
            
            # 查找文章链接
            article_links = soup.find_all('a', href=True)
            if article_links:
                # 分析链接模式
                href_patterns = [link.get('href') for link in article_links[:10]]
                selectors['article_link'] = 'a[href*="news"], a[href*="article"]'
            
            return selectors
            
        except Exception as e:
            print(f"选择器建议失败: {e}")
            return {}
    
    def generate_css_selector(self, element) -> str:
        """生成CSS选择器"""
        if element.get('id'):
            return f"#{element['id']}"
        elif element.get('class'):
            classes = ' '.join(element['class'])
            return f".{classes.replace(' ', '.')}"
        else:
            return element.name
    
    def suggest_article_selectors(self) -> Dict[str, str]:
        """建议文章页面选择器"""
        return {
            'title': 'h1, .title, .headline, [class*="title"]',
            'content': '.content, .article-content, .post-content, [class*="content"]',
            'author': '.author, .byline, [class*="author"]',
            'publish_time': '.time, .date, .publish-time, [class*="time"]',
            'summary': '.summary, .excerpt, .description, [class*="summary"]'
        }
    
    def suggest_pagination_selectors(self) -> Dict[str, str]:
        """建议分页选择器"""
        return {
            'next_page': '.next, .next-page, [class*="next"]',
            'page_numbers': '.page, .pagination a, [class*="page"]'
        }

def main():
    """主函数"""
    print("🤖 智能新闻源发现工具")
    print("=" * 60)
    
    # 示例网站列表
    example_sites = [
        "https://news.sina.com.cn",
        "https://news.qq.com", 
        "https://news.163.com",
        "https://www.36kr.com",
        "https://www.ifanr.com"
    ]
    
    print("📋 示例网站:")
    for i, site in enumerate(example_sites, 1):
        print(f"   {i}. {site}")
    
    print("\n💡 输入要分析的网站URL (或按Enter使用示例):")
    user_input = input("URL: ").strip()
    
    if not user_input:
        # 使用第一个示例网站
        target_url = example_sites[0]
        print(f"🎯 使用示例网站: {target_url}")
    else:
        target_url = user_input
    
    # 开始智能发现
    discovery = SmartSourceDiscovery()
    discovered_sources = discovery.discover_news_sources(target_url)
    
    if discovered_sources:
        print(f"\n🎉 发现 {len(discovered_sources)} 个新闻源:")
        print("=" * 60)
        
        for i, source in enumerate(discovered_sources, 1):
            print(f"\n{i}. {source['name']}")
            print(f"   🌐 URL: {source['url']}")
            print(f"   🔧 类型: {source['type']}")
            print(f"   ⚙️ 解析器: {source['parser']}")
            print(f"   ⏰ 爬取间隔: {source['crawl_interval']} 秒")
            print(f"   🔍 发现方式: {source['discovery_method']}")
            
            if 'config' in source:
                print(f"   ⚙️ 配置: {json.dumps(source['config'], indent=2, ensure_ascii=False)}")
        
        print("\n💡 下一步:")
        print("1. 验证发现的新闻源")
        print("2. 调整爬虫配置")
        print("3. 添加到系统中")
        print("4. 测试爬虫功能")
        
        # 保存发现结果
        with open('discovered_sources.json', 'w', encoding='utf-8') as f:
            json.dump(discovered_sources, f, indent=2, ensure_ascii=False)
        print(f"\n💾 发现结果已保存到: discovered_sources.json")
        
    else:
        print("\n❌ 未发现新闻源，可能原因:")
        print("1. 网站不是新闻网站")
        print("2. 网站结构特殊")
        print("3. 需要手动分析")

if __name__ == "__main__":
    main()
