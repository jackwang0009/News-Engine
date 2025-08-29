"""
新闻数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class NewsSourceType(str, Enum):
    """新闻源类型"""
    WEBSITE = "website"
    RSS = "rss"
    API = "api"
    SOCIAL_MEDIA = "social_media"


class NewsCategory(str, Enum):
    """新闻分类"""
    POLITICS = "politics"
    ECONOMY = "economy"
    TECHNOLOGY = "technology"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    EDUCATION = "education"
    INTERNATIONAL = "international"
    OTHER = "other"


class NewsStatus(str, Enum):
    """新闻状态"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class NewsSource(BaseModel):
    """新闻源模型"""
    id: Optional[str] = None
    name: str = Field(..., description="新闻源名称")
    url: HttpUrl = Field(..., description="新闻源URL")
    type: NewsSourceType = Field(..., description="新闻源类型")
    parser: str = Field(..., description="解析器名称")
    is_active: bool = Field(True, description="是否激活")
    crawl_interval: int = Field(300, description="爬取间隔(秒)")
    last_crawl_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "新浪新闻",
                "url": "https://news.sina.com.cn",
                "type": "website",
                "parser": "sina",
                "crawl_interval": 300
            }
        }


class NewsArticle(BaseModel):
    """新闻文章模型"""
    id: Optional[str] = None
    title: str = Field(..., description="新闻标题")
    content: str = Field(..., description="新闻正文")
    summary: Optional[str] = Field(None, description="新闻摘要")
    url: HttpUrl = Field(..., description="新闻URL")
    source_id: str = Field(..., description="新闻源ID")
    source_name: str = Field(..., description="新闻源名称")
    author: Optional[str] = Field(None, description="作者")
    publish_time: Optional[datetime] = Field(None, description="发布时间")
    crawl_time: datetime = Field(default_factory=datetime.utcnow, description="爬取时间")
    category: Optional[NewsCategory] = Field(None, description="新闻分类")
    tags: List[str] = Field(default_factory=list, description="标签")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    sentiment_score: Optional[float] = Field(None, description="情感得分")
    sentiment_label: Optional[str] = Field(None, description="情感标签")
    image_urls: List[str] = Field(default_factory=list, description="图片URL列表")
    video_urls: List[str] = Field(default_factory=list, description="视频URL列表")
    status: NewsStatus = Field(NewsStatus.DRAFT, description="新闻状态")
    view_count: int = Field(0, description="浏览次数")
    like_count: int = Field(0, description="点赞次数")
    share_count: int = Field(0, description="分享次数")
    comment_count: int = Field(0, description="评论次数")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "title": "人工智能技术取得重大突破",
                "content": "近日，人工智能技术...",
                "url": "https://example.com/news/123",
                "source_id": "sina_001",
                "source_name": "新浪新闻",
                "category": "technology",
                "tags": ["AI", "技术", "突破"]
            }
        }


class NewsSearchResult(BaseModel):
    """新闻搜索结果模型"""
    total: int = Field(..., description="总结果数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    articles: List[NewsArticle] = Field(..., description="新闻文章列表")
    facets: Optional[Dict[str, Any]] = Field(None, description="聚合结果")


class NewsTrend(BaseModel):
    """新闻趋势模型"""
    date: str = Field(..., description="日期")
    count: int = Field(..., description="新闻数量")
    category_counts: Dict[str, int] = Field(default_factory=dict, description="分类统计")
    top_keywords: List[Dict[str, Any]] = Field(default_factory=list, description="热门关键词")


class NewsAnalytics(BaseModel):
    """新闻分析模型"""
    total_articles: int = Field(..., description="总文章数")
    total_sources: int = Field(..., description="总新闻源数")
    today_articles: int = Field(..., description="今日文章数")
    category_distribution: Dict[str, int] = Field(..., description="分类分布")
    source_distribution: Dict[str, int] = Field(..., description="来源分布")
    sentiment_distribution: Dict[str, int] = Field(..., description="情感分布")
    top_keywords: List[Dict[str, Any]] = Field(..., description="热门关键词")
    trending_topics: List[Dict[str, Any]] = Field(..., description="热门话题")
