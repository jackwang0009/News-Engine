"""
请求模式定义
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.news import NewsCategory, NewsSourceType


class NewsSearchRequest(BaseModel):
    """新闻搜索请求"""
    query: Optional[str] = Field(None, description="搜索关键词")
    category: Optional[NewsCategory] = Field(None, description="新闻分类")
    source_id: Optional[str] = Field(None, description="新闻源ID")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小")
    sort_by: str = Field("publish_time", description="排序字段")
    sort_order: str = Field("desc", description="排序顺序")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "人工智能",
                "category": "technology",
                "page": 1,
                "page_size": 20
            }
        }


class NewsSourceCreateRequest(BaseModel):
    """创建新闻源请求"""
    name: str = Field(..., min_length=1, max_length=100, description="新闻源名称")
    url: str = Field(..., description="新闻源URL")
    type: NewsSourceType = Field(..., description="新闻源类型")
    parser: str = Field(..., description="解析器名称")
    crawl_interval: int = Field(300, ge=60, description="爬取间隔(秒)")
    
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


class NewsSourceUpdateRequest(BaseModel):
    """更新新闻源请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="新闻源名称")
    url: Optional[str] = Field(None, description="新闻源URL")
    type: Optional[NewsSourceType] = Field(None, description="新闻源类型")
    parser: Optional[str] = Field(None, description="解析器名称")
    is_active: Optional[bool] = Field(None, description="是否激活")
    crawl_interval: Optional[int] = Field(None, ge=60, description="爬取间隔(秒)")


class CrawlerTaskRequest(BaseModel):
    """爬虫任务请求"""
    source_id: str = Field(..., description="新闻源ID")
    force_crawl: bool = Field(False, description="强制爬取")
    max_pages: Optional[int] = Field(None, ge=1, le=1000, description="最大页数")


class NewsProcessRequest(BaseModel):
    """新闻处理请求"""
    article_ids: List[str] = Field(..., description="文章ID列表")
    process_type: str = Field(..., description="处理类型")
    options: Optional[dict] = Field(None, description="处理选项")


class AnalyticsRequest(BaseModel):
    """分析请求"""
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    group_by: str = Field("day", description="分组方式")
    filters: Optional[dict] = Field(None, description="过滤条件")


class BatchOperationRequest(BaseModel):
    """批量操作请求"""
    operation: str = Field(..., description="操作类型")
    target_ids: List[str] = Field(..., description="目标ID列表")
    parameters: Optional[dict] = Field(None, description="操作参数")
