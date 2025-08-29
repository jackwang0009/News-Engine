# News Engine 项目文档

## 概述

News Engine 是一个全网新闻爬取系统，提供多源新闻采集、数据处理、存储、搜索和分析功能。

## 文档结构

```
docs/
├── README.md              # 本文档
├── architecture/          # 系统架构文档
├── api/                   # API文档
├── deployment/            # 部署文档
├── development/           # 开发指南
├── user-guide/            # 用户指南
└── troubleshooting/       # 故障排除
```

## 快速开始

### 1. 环境准备

- Python 3.11+
- Redis
- PostgreSQL
- MongoDB
- Elasticsearch

### 2. 安装依赖

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 3. 配置环境

```bash
# 复制环境配置模板
cp env.example .env

# 编辑配置文件
vim .env
```

### 4. 启动服务

```bash
# 使用Makefile（推荐）
make start

# 或手动启动
python scripts/start_api.py &
python scripts/start_celery_worker.py &
python scripts/start_celery_beat.py &
```

### 5. 访问服务

- API服务: http://localhost:9000
- API文档: http://localhost:9000/docs
- Flower监控: http://localhost:5555

## 核心功能

### 爬虫模块

- 多源新闻采集
- 智能反爬虫策略
- 分布式爬取
- 实时监控

### 数据处理

- 内容清洗和去重
- NLP分析
- 情感分析
- 关键词提取

### 数据存储

- 关系型数据库（PostgreSQL）
- 文档数据库（MongoDB）
- 搜索引擎（Elasticsearch）
- 缓存（Redis）

### 搜索服务

- 全文搜索
- 智能推荐
- 热点分析
- 趋势预测

## 开发指南

### 代码规范

- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 使用 MyPy 进行类型检查
- 遵循 PEP 8 规范

### 测试

```bash
# 运行所有测试
make test

# 运行测试并生成覆盖率报告
make test-cov

# 运行特定测试
pytest tests/test_crawlers.py -v
```

### 代码质量检查

```bash
# 代码检查
make lint

# 代码格式化
make format
```

## 部署

### Docker部署

```bash
# 构建镜像
make docker-build

# 启动服务
make docker-up

# 查看日志
make docker-logs

# 停止服务
make docker-down
```

### 生产环境

- 使用 Nginx 作为反向代理
- 配置 SSL 证书
- 设置防火墙规则
- 配置监控和告警

## 监控和维护

### 健康检查

```bash
# 检查服务状态
make health-check

# 查看日志
make logs
```

### 性能监控

- 使用 Prometheus 收集指标
- 使用 Grafana 展示仪表板
- 使用 Flower 监控 Celery 任务

## 故障排除

### 常见问题

1. **Redis连接失败**
   - 检查Redis服务状态
   - 验证连接配置

2. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接字符串

3. **爬虫任务失败**
   - 检查网络连接
   - 验证目标网站可访问性
   - 查看错误日志

### 日志分析

```bash
# 查看API日志
tail -f logs/api.log

# 查看Worker日志
tail -f logs/worker.log

# 查看Beat日志
tail -f logs/beat.log
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 讨论交流: [Discussions]

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础爬虫功能
- API服务框架
- 任务调度系统

---

*最后更新: 2024-01-01*
