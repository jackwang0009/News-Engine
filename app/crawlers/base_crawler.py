"""
基础爬虫类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
import random
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import structlog

from app.core.logging import LoggerMixin
from app.config import settings


class BaseCrawler(ABC, LoggerMixin):
    """基础爬虫抽象类"""
    
    def __init__(self, source_id: str, source_url: str, **kwargs):
        super().__init__()
        self.source_id = source_id
        self.source_url = source_url
        self.session = requests.Session()
        self.setup_session()
        
        # 爬虫配置
        self.delay = kwargs.get('delay', settings.CRAWLER_DELAY)
        self.timeout = kwargs.get('timeout', settings.CRAWLER_TIMEOUT)
        self.max_retries = kwargs.get('max_retries', settings.CRAWLER_MAX_RETRIES)
        self.max_pages = kwargs.get('max_pages', 10)
        
        # 状态跟踪
        self.articles_found = 0
        self.articles_processed = 0
        self.errors = []
        self.start_time = None
        
    def setup_session(self):
        """设置请求会话"""
        # 设置User-Agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 设置代理（如果启用）
        if settings.PROXY_ENABLED and settings.PROXY_URL:
            self.session.proxies = {
                'http': settings.PROXY_URL,
                'https': settings.PROXY_URL
            }
    
    def get_page(self, url: str, retries: int = 0) -> Optional[requests.Response]:
        """获取页面内容"""
        try:
            self.log_info(f"Fetching page: {url}")
            
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # 添加延迟
            time.sleep(self.delay)
            
            return response
            
        except requests.RequestException as e:
            self.log_error(f"Failed to fetch page {url}: {str(e)}")
            
            if retries < self.max_retries:
                self.log_info(f"Retrying {url} (attempt {retries + 1}/{self.max_retries})")
                time.sleep(self.delay * (retries + 1))  # 指数退避
                return self.get_page(url, retries + 1)
            else:
                self.errors.append({
                    'url': url,
                    'error': str(e),
                    'retries': retries
                })
                return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """解析HTML内容"""
        return BeautifulSoup(html_content, 'lxml')
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """提取页面中的链接"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            # 过滤链接
            if self.is_valid_link(absolute_url):
                links.append(absolute_url)
        
        return list(set(links))  # 去重
    
    def is_valid_link(self, url: str) -> bool:
        """检查链接是否有效"""
        try:
            parsed = urlparse(url)
            
            # 检查协议
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # 检查域名（可以添加更多过滤规则）
            if not parsed.netloc:
                return False
            
            # 过滤特定文件类型
            excluded_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar']
            if any(url.lower().endswith(ext) for ext in excluded_extensions):
                return False
            
            return True
            
        except Exception:
            return False
    
    @abstractmethod
    def extract_articles(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """提取文章信息（子类必须实现）"""
        pass
    
    @abstractmethod
    def get_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """获取下一页URL（子类必须实现）"""
        pass
    
    def crawl(self) -> Dict[str, Any]:
        """执行爬虫任务"""
        self.start_time = time.time()
        self.log_info(f"Starting crawler for source: {self.source_id}")
        
        all_articles = []
        current_url = self.source_url
        page_count = 0
        
        try:
            while current_url and page_count < self.max_pages:
                self.log_info(f"Crawling page {page_count + 1}: {current_url}")
                
                # 获取页面
                response = self.get_page(current_url)
                if not response:
                    break
                
                # 解析HTML
                soup = self.parse_html(response.text)
                
                # 提取文章
                articles = self.extract_articles(soup, current_url)
                all_articles.extend(articles)
                self.articles_found += len(articles)
                
                # 获取下一页
                current_url = self.get_next_page_url(soup, current_url)
                page_count += 1
                
                self.log_info(f"Page {page_count} completed, found {len(articles)} articles")
        
        except Exception as e:
            self.log_error(f"Crawler error: {str(e)}")
            self.errors.append({
                'type': 'crawler_error',
                'error': str(e),
                'page': page_count
            })
        
        finally:
            # 统计结果
            crawl_time = time.time() - self.start_time
            self.articles_processed = len(all_articles)
            
            result = {
                'source_id': self.source_id,
                'source_url': self.source_url,
                'articles_found': self.articles_found,
                'articles_processed': self.articles_processed,
                'pages_crawled': page_count,
                'crawl_time': crawl_time,
                'errors': self.errors,
                'articles': all_articles
            }
            
            self.log_info(
                f"Crawler completed",
                articles_found=self.articles_found,
                pages_crawled=page_count,
                crawl_time=crawl_time
            )
            
            return result
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class RSSFeedCrawler(BaseCrawler):
    """RSS订阅爬虫"""
    
    def __init__(self, source_id: str, source_url: str, **kwargs):
        super().__init__(source_id, source_url, **kwargs)
        import feedparser
        self.feedparser = feedparser
    
    def extract_articles(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """从RSS源提取文章"""
        articles = []
        
        try:
            feed = self.feedparser.parse(page_url)
            
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', ''),
                    'content': entry.get('summary', ''),
                    'url': entry.get('link', ''),
                    'publish_time': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'source_id': self.source_id,
                    'source_url': self.source_url
                }
                articles.append(article)
        
        except Exception as e:
            self.log_error(f"Failed to parse RSS feed: {str(e)}")
        
        return articles
    
    def get_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """RSS通常只有一页"""
        return None


class WebsiteCrawler(BaseCrawler):
    """网站爬虫基类"""
    
    def __init__(self, source_id: str, source_url: str, **kwargs):
        super().__init__(source_id, source_url, **kwargs)
        
        # 网站特定配置
        self.article_selectors = kwargs.get('article_selectors', {})
        self.pagination_selectors = kwargs.get('pagination_selectors', {})
        self.content_selectors = kwargs.get('content_selectors', {})
    
    def extract_articles(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """从网页提取文章（需要子类实现具体逻辑）"""
        raise NotImplementedError("Subclasses must implement extract_articles")
    
    def get_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """获取下一页URL（需要子类实现具体逻辑）"""
        raise NotImplementedError("Subclasses must implement get_next_page_url")
