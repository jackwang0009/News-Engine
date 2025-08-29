# News Engine API 文档

## 概述

News Engine 提供完整的 RESTful API 接口，支持新闻数据的查询、管理、爬虫控制和分析功能。

## 基础信息

- **Base URL**: `http://localhost:9000`
- **API Version**: `v1`
- **认证方式**: JWT Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

### JWT Token 认证

```http
Authorization: Bearer <your_jwt_token>
```

### 获取 Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

## 通用响应格式

### 成功响应

```json
{
  "status": "success",
  "data": {...},
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 错误响应

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": [...]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |

## 分页参数

### 查询参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码，从1开始 |
| size | integer | 20 | 每页数量，最大100 |
| sort | string | "created_at" | 排序字段 |
| order | string | "desc" | 排序方向：asc/desc |

### 分页响应

```json
{
  "status": "success",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## API 端点

### 1. 健康检查

#### 基础健康检查

```http
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

#### 详细健康检查

```http
GET /health/detailed
```

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "elasticsearch": "healthy"
  },
  "system": {
    "cpu_usage": 15.2,
    "memory_usage": 45.8,
    "disk_usage": 23.1
  }
}
```

### 2. 新闻管理

#### 搜索新闻

```http
GET /api/v1/news/
```

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| q | string | 搜索关键词 |
| category | string | 新闻分类 |
| source | string | 新闻来源 |
| start_date | string | 开始日期 (YYYY-MM-DD) |
| end_date | string | 结束日期 (YYYY-MM-DD) |
| sentiment | string | 情感倾向 (positive/negative/neutral) |

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "total": 150,
    "articles": [
      {
        "id": "article_001",
        "title": "新闻标题",
        "content": "新闻内容摘要...",
        "url": "https://example.com/news/001",
        "source": "新浪新闻",
        "category": "科技",
        "publish_time": "2024-01-01T10:00:00Z",
        "sentiment": "positive",
        "keywords": ["AI", "技术", "创新"]
      }
    ],
    "pagination": {...}
  }
}
```

#### 获取新闻详情

```http
GET /api/v1/news/{article_id}
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "id": "article_001",
    "title": "新闻标题",
    "content": "完整的新闻内容...",
    "url": "https://example.com/news/001",
    "source": "新浪新闻",
    "category": "科技",
    "publish_time": "2024-01-01T10:00:00Z",
    "sentiment": "positive",
    "sentiment_score": 0.8,
    "keywords": ["AI", "技术", "创新"],
    "author": "记者姓名",
    "tags": ["标签1", "标签2"],
    "related_articles": [...]
  }
}
```

#### 获取热门新闻

```http
GET /api/v1/news/trending
```

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| period | string | "24h" | 时间周期：1h, 24h, 7d, 30d |
| limit | integer | 10 | 返回数量 |

#### 获取最新新闻

```http
GET /api/v1/news/latest
```

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | integer | 20 | 返回数量 |
| category | string | null | 新闻分类 |

### 3. 新闻源管理

#### 获取新闻源列表

```http
GET /api/v1/sources/
```

**响应示例**:
```json
{
  "status": "success",
  "data": [
    {
      "id": "source_001",
      "name": "新浪新闻",
      "url": "https://news.sina.com.cn",
      "type": "website",
      "status": "active",
      "last_crawl": "2024-01-01T09:00:00Z",
      "crawl_count": 1250,
      "success_rate": 95.2
    }
  ]
}
```

#### 创建新闻源

```http
POST /api/v1/sources/
Content-Type: application/json

{
  "name": "新新闻源",
  "url": "https://example.com",
  "type": "website",
  "selectors": {
    "title": "h1.title",
    "content": ".content",
    "author": ".author"
  }
}
```

#### 更新新闻源

```http
PUT /api/v1/sources/{source_id}
Content-Type: application/json

{
  "name": "更新后的名称",
  "status": "inactive"
}
```

#### 删除新闻源

```http
DELETE /api/v1/sources/{source_id}
```

#### 测试新闻源

```http
POST /api/v1/sources/{source_id}/test
```

#### 激活/停用新闻源

```http
POST /api/v1/sources/{source_id}/activate
POST /api/v1/sources/{source_id}/deactivate
```

### 4. 爬虫管理

#### 获取爬虫状态

```http
GET /api/v1/crawlers/status
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "total_sources": 25,
    "active_sources": 20,
    "overall_status": "healthy",
    "last_crawl": "2024-01-01T09:00:00Z",
    "crawl_stats": {
      "total_articles": 12500,
      "today_articles": 150,
      "success_rate": 94.5,
      "error_count": 68
    }
  }
}
```

#### 获取爬虫任务列表

```http
GET /api/v1/crawlers/tasks
```

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | 任务状态 |
| source_id | string | 新闻源ID |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |

#### 启动爬虫任务

```http
POST /api/v1/crawlers/start
Content-Type: application/json

{
  "source_id": "source_001",
  "crawl_type": "full",
  "priority": "high"
}
```

#### 停止爬虫任务

```http
POST /api/v1/crawlers/stop
Content-Type: application/json

{
  "source_id": "source_001"
}
```

#### 获取任务状态

```http
GET /api/v1/crawlers/tasks/{task_id}
```

#### 批量启动爬虫

```http
POST /api/v1/crawlers/batch-start
Content-Type: application/json

{
  "source_ids": ["source_001", "source_002"],
  "crawl_type": "incremental"
}
```

#### 获取爬虫统计

```http
GET /api/v1/crawlers/statistics
```

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| period | string | "7d" | 统计周期 |
| group_by | string | "source" | 分组方式 |

### 5. 数据分析

#### 获取概览数据

```http
GET /api/v1/analytics/overview
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "total_articles": 12500,
    "total_sources": 25,
    "today_articles": 150,
    "active_sources": 20,
    "categories_distribution": {
      "科技": 25.5,
      "政治": 18.2,
      "经济": 22.1,
      "社会": 34.2
    },
    "sentiment_distribution": {
      "positive": 45.2,
      "neutral": 38.1,
      "negative": 16.7
    }
  }
}
```

#### 获取趋势数据

```http
GET /api/v1/analytics/trends
```

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| metric | string | "article_count" | 指标类型 |
| period | string | "7d" | 时间周期 |
| interval | string | "1d" | 时间间隔 |

#### 获取情感分析

```http
GET /api/v1/analytics/sentiment
```

**查询参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| category | string | 新闻分类 |
| source | string | 新闻来源 |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |

#### 获取关键词分析

```http
GET /api/v1/analytics/keywords
```

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| period | string | "7d" | 时间周期 |
| limit | integer | 20 | 返回数量 |
| min_frequency | integer | 5 | 最小频率 |

#### 获取来源性能

```http
GET /api/v1/analytics/source-performance
```

#### 自定义查询

```http
POST /api/v1/analytics/custom-query
Content-Type: application/json

{
  "query": "SELECT category, COUNT(*) as count FROM articles WHERE publish_time >= '2024-01-01' GROUP BY category",
  "parameters": {}
}
```

## 错误处理

### 常见错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| VALIDATION_ERROR | 422 | 参数验证失败 |
| AUTHENTICATION_ERROR | 401 | 认证失败 |
| AUTHORIZATION_ERROR | 403 | 权限不足 |
| RESOURCE_NOT_FOUND | 404 | 资源不存在 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### 错误响应示例

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": [
      {
        "field": "url",
        "message": "URL格式不正确"
      }
    ]
  }
}
```

## 限流策略

### 限流规则

- **普通用户**: 100次/分钟
- **认证用户**: 1000次/分钟
- **高级用户**: 5000次/分钟

### 限流响应

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求频率超限，请稍后重试",
    "retry_after": 60
  }
}
```

## 版本控制

### 版本策略

- 使用语义化版本号 (Semantic Versioning)
- 主版本号变更可能包含破坏性更改
- 次版本号添加新功能，保持向后兼容
- 修订版本号修复bug，保持向后兼容

### 版本弃用

- 弃用的API端点会返回警告头
- 弃用信息包含在响应中
- 提供迁移指南和替代方案

## 测试

### 测试环境

- **测试URL**: `http://test-api.news-engine.com`
- **测试数据**: 使用模拟数据，不影响生产环境
- **认证**: 使用测试账号和Token

### 测试工具

- **Postman**: API测试集合
- **curl**: 命令行测试
- **Swagger UI**: 交互式API文档

## 支持

### 技术支持

- **文档**: 本文档和在线API文档
- **示例**: GitHub仓库中的代码示例
- **社区**: 开发者论坛和讨论组

### 联系方式

- **邮箱**: api-support@news-engine.com
- **GitHub**: [Issues](https://github.com/news-engine/issues)
- **文档**: [API文档](https://docs.news-engine.com/api)

---

*最后更新: 2024-01-01*
