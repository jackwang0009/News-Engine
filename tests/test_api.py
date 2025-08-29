"""
API测试文件
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_news_search():
    """测试新闻搜索端点"""
    response = client.get("/api/v1/news/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "articles" in data


def test_news_sources():
    """测试新闻源端点"""
    response = client.get("/api/v1/sources/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_crawler_status():
    """测试爬虫状态端点"""
    response = client.get("/api/v1/crawlers/status")
    assert response.status_code == 200
    data = response.json()
    assert "total_sources" in data
    assert "overall_status" in data


def test_analytics_overview():
    """测试分析概览端点"""
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_articles" in data
    assert "total_sources" in data


if __name__ == "__main__":
    pytest.main([__file__])
