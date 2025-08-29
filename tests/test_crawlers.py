"""
爬虫测试文件
"""
import pytest
from unittest.mock import Mock, patch
from app.crawlers.sina_crawler import SinaCrawler
from app.crawlers.tencent_crawler import TencentCrawler


class TestSinaCrawler:
    """新浪爬虫测试类"""
    
    def setup_method(self):
        """设置测试方法"""
        self.crawler = SinaCrawler("test_sina", "https://news.sina.com.cn")
    
    def test_clean_text(self):
        """测试文本清理"""
        text = "  测试文本  \n\n  包含换行  "
        cleaned = self.crawler.clean_text(text)
        assert cleaned == "测试文本 包含换行"
    
    def test_parse_publish_time(self):
        """测试发布时间解析"""
        time_str = "2024-01-01 10:30"
        parsed = self.crawler.parse_publish_time(time_str)
        assert parsed == time_str
    
    def test_is_valid_next_page_url(self):
        """测试下一页URL验证"""
        current_url = "https://news.sina.com.cn/news/1.html"
        next_url = "https://news.sina.com.cn/news/2.html"
        
        assert self.crawler.is_valid_next_page_url(next_url, current_url) == True
        
        # 测试不同域名
        invalid_url = "https://other.com/news/2.html"
        assert self.crawler.is_valid_next_page_url(invalid_url, current_url) == False


class TestTencentCrawler:
    """腾讯爬虫测试类"""
    
    def setup_method(self):
        """设置测试方法"""
        self.crawler = TencentCrawler("test_tencent", "https://news.qq.com")
    
    def test_clean_text(self):
        """测试文本清理"""
        text = "  腾讯新闻  \n\n  测试内容  "
        cleaned = self.crawler.clean_text(text)
        assert cleaned == "腾讯新闻 测试内容"
    
    def test_parse_publish_time(self):
        """测试发布时间解析"""
        time_str = "刚刚"
        parsed = self.crawler.parse_publish_time(time_str)
        assert parsed == time_str
    
    def test_infer_next_page_url(self):
        """测试下一页URL推断"""
        current_url = "https://news.qq.com/news/1.html"
        next_url = self.crawler.infer_next_page_url(current_url)
        assert next_url == "https://news.qq.com/news/2.html"


def test_crawler_inheritance():
    """测试爬虫继承关系"""
    sina_crawler = SinaCrawler("test", "https://test.com")
    tencent_crawler = TencentCrawler("test", "https://test.com")
    
    # 检查是否都继承自WebsiteCrawler
    from app.crawlers.base_crawler import WebsiteCrawler
    assert isinstance(sina_crawler, WebsiteCrawler)
    assert isinstance(tencent_crawler, WebsiteCrawler)


if __name__ == "__main__":
    pytest.main([__file__])
