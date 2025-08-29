"""
新浪新闻爬虫
"""
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

from app.crawlers.base_crawler import WebsiteCrawler
from app.core.logging import LoggerMixin


class SinaCrawler(WebsiteCrawler):
    """新浪新闻爬虫"""
    
    def __init__(self, source_id: str, source_url: str, **kwargs):
        super().__init__(source_id, source_url, **kwargs)
        
        # 新浪新闻特定的选择器
        self.article_selectors = {
            'news_list': '.news-item, .news-card, .feed-item',
            'title': 'h1, h2, h3, .title, .headline',
            'content': '.article-content, .content, .summary',
            'author': '.author, .reporter, .writer',
            'publish_time': '.time, .date, .publish-time',
            'category': '.category, .channel, .tag'
        }
        
        self.pagination_selectors = {
            'next_page': '.next, .pagination .next, a[rel="next"]',
            'page_numbers': '.pagination a, .page-num a'
        }
    
    def extract_articles(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """从新浪新闻页面提取文章"""
        articles = []
        
        try:
            # 查找新闻列表
            news_items = soup.select(self.article_selectors['news_list'])
            
            if not news_items:
                # 尝试其他选择器
                news_items = soup.select('article, .news, .post')
            
            for item in news_items:
                try:
                    article = self.extract_article_data(item, page_url)
                    if article:
                        articles.append(article)
                except Exception as e:
                    self.log_error(f"Failed to extract article data: {str(e)}")
                    continue
            
            # 如果没有找到文章，尝试从页面直接提取
            if not articles:
                article = self.extract_from_page(soup, page_url)
                if article:
                    articles.append(article)
        
        except Exception as e:
            self.log_error(f"Failed to extract articles: {str(e)}")
        
        return articles
    
    def extract_article_data(self, item: BeautifulSoup, page_url: str) -> Optional[Dict[str, Any]]:
        """提取文章数据"""
        try:
            # 提取标题
            title = self.extract_text(item, self.article_selectors['title'])
            
            # 提取链接
            link = self.extract_link(item, page_url)
            
            # 提取摘要/内容
            content = self.extract_text(item, self.article_selectors['content'])
            
            # 提取作者
            author = self.extract_text(item, self.article_selectors['author'])
            
            # 提取发布时间
            publish_time = self.extract_text(item, self.article_selectors['publish_time'])
            
            # 提取分类
            category = self.extract_text(item, self.article_selectors['category'])
            
            # 验证必要字段
            if not title or not link:
                return None
            
            # 清理和格式化数据
            title = self.clean_text(title)
            content = self.clean_text(content)
            author = self.clean_text(author)
            category = self.clean_text(category)
            
            # 解析发布时间
            parsed_time = self.parse_publish_time(publish_time)
            
            article = {
                'title': title,
                'content': content or '',
                'url': link,
                'author': author,
                'publish_time': parsed_time,
                'category': category,
                'source_id': self.source_id,
                'source_name': '新浪新闻',
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            return article
        
        except Exception as e:
            self.log_error(f"Failed to extract article data: {str(e)}")
            return None
    
    def extract_from_page(self, soup: BeautifulSoup, page_url: str) -> Optional[Dict[str, Any]]:
        """从页面直接提取文章信息"""
        try:
            # 尝试从页面标题和内容提取
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else ''
            
            # 查找主要内容
            content_selectors = [
                '.article-content',
                '.content',
                '.main-content',
                'article',
                '.post-content'
            ]
            
            content = ''
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    break
            
            if title_text and content:
                return {
                    'title': self.clean_text(title_text),
                    'content': self.clean_text(content),
                    'url': page_url,
                    'source_id': self.source_id,
                    'source_name': '新浪新闻',
                    'extracted_at': datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            self.log_error(f"Failed to extract from page: {str(e)}")
        
        return None
    
    def get_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """获取下一页URL"""
        try:
            # 尝试多种分页选择器
            for selector in self.pagination_selectors.values():
                next_link = soup.select_one(selector)
                if next_link and next_link.get('href'):
                    next_url = next_link['href']
                    absolute_url = urljoin(current_url, next_url)
                    
                    # 验证URL是否有效
                    if self.is_valid_next_page_url(absolute_url, current_url):
                        return absolute_url
            
            # 尝试从URL模式推断下一页
            next_url = self.infer_next_page_url(current_url)
            if next_url:
                return next_url
        
        except Exception as e:
            self.log_error(f"Failed to get next page URL: {str(e)}")
        
        return None
    
    def is_valid_next_page_url(self, next_url: str, current_url: str) -> bool:
        """验证下一页URL是否有效"""
        try:
            current_parsed = urlparse(current_url)
            next_parsed = urlparse(next_url)
            
            # 检查是否是同一个域名
            if current_parsed.netloc != next_parsed.netloc:
                return False
            
            # 检查是否是新闻页面
            if 'news' not in next_parsed.path.lower():
                return False
            
            # 避免重复页面
            if next_url == current_url:
                return False
            
            return True
        
        except Exception:
            return False
    
    def infer_next_page_url(self, current_url: str) -> Optional[str]:
        """从URL模式推断下一页"""
        try:
            # 新浪新闻常见的分页模式
            patterns = [
                r'(\d+)\.s?html?$',  # 数字.html
                r'page=(\d+)',        # page=数字
                r'p=(\d+)',           # p=数字
            ]
            
            for pattern in patterns:
                match = re.search(pattern, current_url)
                if match:
                    current_page = int(match.group(1))
                    next_page = current_page + 1
                    
                    # 替换页码
                    next_url = re.sub(pattern, str(next_page), current_url)
                    
                    # 验证URL
                    if self.is_valid_next_page_url(next_url, current_url):
                        return next_url
            
        except Exception as e:
            self.log_error(f"Failed to infer next page URL: {str(e)}")
        
        return None
    
    def clean_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff\-\.\,\!\?]', '', text)
        
        return text
    
    def parse_publish_time(self, time_str: str) -> Optional[str]:
        """解析发布时间"""
        if not time_str:
            return None
        
        try:
            # 新浪新闻常见的时间格式
            time_patterns = [
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{2}-\d{2})',
                r'(\d{2}:\d{2})',
                r'(\d{1,2}小时前)',
                r'(\d{1,2}分钟前)'
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, time_str)
                if match:
                    # 这里可以添加更复杂的时间解析逻辑
                    return time_str
            
            return time_str
        
        except Exception:
            return time_str
