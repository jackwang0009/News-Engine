# 全网新闻爬取系统 (News Engine)

一个高性能、可扩展的分布式新闻爬虫系统，支持多源新闻抓取、数据清洗、存储和可视化分析。

## 🚀 特性

- **多源抓取**: 支持新闻网站、聚合平台、社交媒体、RSS订阅
- **智能解析**: 自动提取新闻标题、正文、时间、作者等结构化信息
- **分布式架构**: 基于Celery的任务调度，支持水平扩展
- **数据清洗**: NLP分析、去重、情感分析
- **全文搜索**: 基于Elasticsearch的高性能搜索
- **实时监控**: 任务状态监控、性能指标统计
- **可视化**: 新闻热度分析、趋势图表

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   爬虫模块      │    │   任务调度      │    │   数据存储      │
│  - Scrapy      │───▶│  - Celery      │───▶│  - PostgreSQL  │
│  - Selenium    │    │  - Redis       │    │  - MongoDB     │
│  - Playwright  │    │  - Flower      │    │  - Elasticsearch│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   数据清洗      │    │   API服务       │
                       │  - NLP分析     │    │  - FastAPI     │
                       │  - 去重        │    │  - 搜索接口     │
                       │  - 情感分析    │    │  - 数据接口     │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ 技术栈

- **后端**: FastAPI, Celery, Redis
- **爬虫**: Scrapy, Selenium, Playwright, Newspaper3k
- **数据库**: PostgreSQL, MongoDB, Elasticsearch, Redis
- **任务调度**: Celery + Redis
- **监控**: Flower, Prometheus
- **测试**: pytest

## 📦 安装

1. 克隆项目
```bash
git clone <repository-url>
cd News_Engine
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 安装Playwright浏览器
```bash
playwright install
```

## 🚀 快速开始

1. 启动Redis服务
```bash
redis-server
```

2. 启动Celery Worker
```bash
celery -A app.celery_app worker --loglevel=info
```

3. 启动Celery Beat (定时任务)
```bash
celery -A app.celery_app beat --loglevel=info
```

4. 启动API服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

5. 启动Flower监控 (可选)
```bash
celery -A app.celery_app flower
```

## 📁 项目结构

```
News_Engine/
├── app/                    # 主应用目录
│   ├── __init__.py
│   ├── main.py            # FastAPI主应用
│   ├── celery_app.py      # Celery配置
│   ├── config.py          # 配置文件
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic模式
│   ├── api/               # API路由
│   ├── core/              # 核心功能
│   ├── crawlers/          # 爬虫模块
│   ├── processors/        # 数据处理
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── tests/                 # 测试文件
├── scripts/               # 脚本文件
├── docker/                # Docker配置
├── requirements.txt        # 依赖文件
└── README.md              # 项目说明
```

## 🔧 配置

复制配置文件模板并修改：

```bash
cp app/config.py.example app/config.py
```

主要配置项：
- 数据库连接
- Redis配置
- 爬虫设置
- API密钥

## 📊 使用示例

### 1. 添加新闻源
```python
from app.services.news_source_service import NewsSourceService

source_service = NewsSourceService()
source_service.add_source(
    name="新浪新闻",
    url="https://news.sina.com.cn",
    type="website",
    parser="sina"
)
```

### 2. 启动爬虫任务
```python
from app.tasks.crawler_tasks import start_crawler_task

# 启动爬虫任务
start_crawler_task.delay("sina")
```

### 3. 搜索新闻
```python
from app.services.search_service import SearchService

search_service = SearchService()
results = search_service.search(
    query="人工智能",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_crawlers/

# 生成覆盖率报告
pytest --cov=app tests/
```

## 📈 监控

- **Flower**: http://localhost:5555 (Celery任务监控)
- **API文档**: http://localhost:9000/docs
- **健康检查**: http://localhost:9000/health

## 🤝 贡献

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## ⚠️ 免责声明

本项目仅用于学习和研究目的。请遵守目标网站的robots.txt和使用条款，合理控制爬取频率，避免对目标网站造成过大压力。使用者需自行承担因使用本项目而产生的任何法律责任。
