# News Engine Makefile
# 用于项目管理和构建的便捷命令

.PHONY: help install install-dev test test-cov lint format clean start stop restart docker-build docker-up docker-down docker-logs

# 默认目标
help:
	@echo "News Engine 项目管理命令"
	@echo ""
	@echo "安装和依赖:"
	@echo "  install      - 安装生产依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo ""
	@echo "代码质量:"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  test         - 运行测试"
	@echo "  test-cov     - 运行测试并生成覆盖率报告"
	@echo ""
	@echo "服务管理:"
	@echo "  start        - 启动所有服务"
	@echo "  stop         - 停止所有服务"
	@echo "  restart      - 重启所有服务"
	@echo ""
	@echo "Docker管理:"
	@echo "  docker-build - 构建Docker镜像"
	@echo "  docker-up    - 启动Docker服务"
	@echo "  docker-down  - 停止Docker服务"
	@echo "  docker-logs  - 查看Docker日志"
	@echo ""
	@echo "维护:"
	@echo "  clean        - 清理临时文件"
	@echo "  logs         - 查看日志"

# 安装生产依赖
install:
	@echo "安装生产依赖..."
	pip install -r requirements.txt

# 安装开发依赖
install-dev:
	@echo "安装开发依赖..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# 代码检查
lint:
	@echo "运行代码检查..."
	flake8 app/ tests/ --max-line-length=100 --ignore=E203,W503
	mypy app/ --ignore-missing-imports
	black --check app/ tests/

# 代码格式化
format:
	@echo "格式化代码..."
	black app/ tests/
	isort app/ tests/

# 运行测试
test:
	@echo "运行测试..."
	pytest tests/ -v

# 运行测试并生成覆盖率报告
test-cov:
	@echo "运行测试并生成覆盖率报告..."
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# 启动所有服务
start:
	@echo "启动所有服务..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		start.bat; \
	else \
		chmod +x scripts/start_all.sh && ./scripts/start_all.sh; \
	fi

# 停止所有服务
stop:
	@echo "停止所有服务..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		stop_all.bat; \
	else \
		chmod +x scripts/stop_all.sh && ./scripts/stop_all.sh; \
	fi

# 重启所有服务
restart: stop start

# 构建Docker镜像
docker-build:
	@echo "构建Docker镜像..."
	docker build -t news-engine .

# 启动Docker服务
docker-up:
	@echo "启动Docker服务..."
	docker-compose up -d

# 停止Docker服务
docker-down:
	@echo "停止Docker服务..."
	docker-compose down

# 查看Docker日志
docker-logs:
	@echo "查看Docker日志..."
	docker-compose logs -f

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "*.pid" -delete
	rm -rf build/ dist/ logs/ uploads/

# 查看日志
logs:
	@echo "查看日志文件..."
	@if [ -d "logs" ]; then \
		echo "最近的日志:"; \
		ls -la logs/; \
		echo ""; \
		echo "API日志:"; \
		tail -f logs/api.log 2>/dev/null || echo "API日志文件不存在"; \
	else \
		echo "日志目录不存在"; \
	fi

# 创建必要的目录
setup-dirs:
	@echo "创建必要的目录..."
	mkdir -p logs uploads temp

# 初始化数据库
init-db:
	@echo "初始化数据库..."
	@echo "请确保数据库服务已启动"
	@echo "PostgreSQL: docker-compose up postgres -d"
	@echo "MongoDB: docker-compose up mongodb -d"
	@echo "Redis: docker-compose up redis -d"
	@echo "Elasticsearch: docker-compose up elasticsearch -d"

# 健康检查
health-check:
	@echo "检查服务健康状态..."
	@curl -s http://localhost:9000/health || echo "API服务未运行"
	@curl -s http://localhost:5555 || echo "Flower监控未运行"
	@redis-cli ping 2>/dev/null || echo "Redis未运行"

# 部署准备
deploy-prep:
	@echo "准备部署..."
	@echo "1. 更新依赖..."
	pip install -r requirements.txt
	@echo "2. 运行测试..."
	make test
	@echo "3. 代码检查..."
	make lint
	@echo "4. 构建Docker镜像..."
	make docker-build
	@echo "部署准备完成！"

# 开发环境设置
dev-setup: setup-dirs install-dev
	@echo "开发环境设置完成！"
	@echo "运行 'make start' 启动所有服务"
	@echo "运行 'make test' 运行测试"
	@echo "运行 'make lint' 检查代码质量"
