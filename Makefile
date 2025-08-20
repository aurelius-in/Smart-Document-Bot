# AI Document Agent - Development Makefile
# Provides convenient commands for development, testing, and deployment

.PHONY: help install test lint format clean build deploy docker-build docker-run docker-stop

# Default target
help:
	@echo "AI Document Agent - Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Installation:"
	@echo "  install          Install all dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  install-prod     Install production dependencies"
	@echo ""
	@echo "Development:"
	@echo "  dev              Start development servers"
	@echo "  dev-backend      Start backend development server"
	@echo "  dev-frontend     Start frontend development server"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage    Run tests with coverage report"
	@echo "  test-load        Run load tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint             Run all linting checks"
	@echo "  lint-backend     Lint backend code"
	@echo "  lint-frontend    Lint frontend code"
	@echo "  format           Format all code"
	@echo "  format-backend   Format backend code"
	@echo "  format-frontend  Format frontend code"
	@echo ""
	@echo "Database:"
	@echo "  db-init          Initialize database"
	@echo "  db-migrate       Run database migrations"
	@echo "  db-reset         Reset database"
	@echo "  db-backup        Create database backup"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build     Build Docker images"
	@echo "  docker-run       Run with Docker Compose"
	@echo "  docker-stop      Stop Docker containers"
	@echo "  docker-clean     Clean Docker resources"
	@echo ""
	@echo "Deployment:"
	@echo "  build            Build for production"
	@echo "  deploy-staging   Deploy to staging"
	@echo "  deploy-prod      Deploy to production"
	@echo ""
	@echo "Monitoring:"
	@echo "  monitoring-start Start monitoring stack"
	@echo "  monitoring-stop  Stop monitoring stack"
	@echo ""
	@echo "Utilities:"
	@echo "  clean            Clean build artifacts"
	@echo "  logs             Show application logs"
	@echo "  health           Check system health"

# Installation
install: install-backend install-frontend
	@echo "✅ All dependencies installed"

install-backend:
	@echo "📦 Installing backend dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install

install-dev: install-backend install-frontend
	@echo "📦 Installing development dependencies..."
	pip install -r requirements-dev.txt
	cd frontend && npm install --include=dev

install-prod: install-backend install-frontend
	@echo "📦 Installing production dependencies..."
	cd frontend && npm ci --only=production

# Development
dev: dev-backend dev-frontend
	@echo "🚀 Development servers started"

dev-backend:
	@echo "🚀 Starting backend development server..."
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "🚀 Starting frontend development server..."
	cd frontend && npm start

# Testing
test: test-backend test-frontend
	@echo "✅ All tests completed"

test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && pytest tests/ -v

test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && npm test -- --watchAll=false

test-unit:
	@echo "🧪 Running unit tests..."
	cd backend && pytest tests/ -m "unit" -v

test-integration:
	@echo "🧪 Running integration tests..."
	cd backend && pytest tests/ -m "integration" -v

test-coverage:
	@echo "🧪 Running tests with coverage..."
	cd backend && pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
	cd frontend && npm test -- --coverage --watchAll=false

test-load:
	@echo "🧪 Running load tests..."
	cd backend && locust -f tests/load/locustfile.py --headless --users 10 --spawn-rate 2 --run-time 60s

# Code Quality
lint: lint-backend lint-frontend
	@echo "✅ All linting checks completed"

lint-backend:
	@echo "🔍 Linting backend code..."
	cd backend && flake8 app/ --max-line-length=88 --extend-ignore=E203,W503
	cd backend && black --check app/
	cd backend && isort --check-only app/
	cd backend && mypy app/

lint-frontend:
	@echo "🔍 Linting frontend code..."
	cd frontend && npm run lint
	cd frontend && npm run type-check

format: format-backend format-frontend
	@echo "✨ All code formatted"

format-backend:
	@echo "✨ Formatting backend code..."
	cd backend && black app/
	cd backend && isort app/

format-frontend:
	@echo "✨ Formatting frontend code..."
	cd frontend && npm run format

# Database
db-init:
	@echo "🗄️ Initializing database..."
	cd backend && python -c "from app.database.connection import init_database; import asyncio; asyncio.run(init_database())"

db-migrate:
	@echo "🗄️ Running database migrations..."
	cd backend && alembic upgrade head

db-reset:
	@echo "🗄️ Resetting database..."
	cd backend && alembic downgrade base
	cd backend && alembic upgrade head
	cd backend && python -c "from app.database.connection import initialize_default_data; import asyncio; asyncio.run(initialize_default_data())"

db-backup:
	@echo "🗄️ Creating database backup..."
	./scripts/backup.sh

# Docker
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-run:
	@echo "🐳 Starting Docker containers..."
	docker-compose up -d

docker-stop:
	@echo "🐳 Stopping Docker containers..."
	docker-compose down

docker-clean:
	@echo "🐳 Cleaning Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Deployment
build: build-backend build-frontend
	@echo "🏗️ Production build completed"

build-backend:
	@echo "🏗️ Building backend..."
	cd backend && python -m build

build-frontend:
	@echo "🏗️ Building frontend..."
	cd frontend && npm run build

deploy-staging:
	@echo "🚀 Deploying to staging..."
	./scripts/deploy.sh staging

deploy-prod:
	@echo "🚀 Deploying to production..."
	./scripts/deploy.sh production

# Monitoring
monitoring-start:
	@echo "📊 Starting monitoring stack..."
	./scripts/monitoring-setup.sh start

monitoring-stop:
	@echo "📊 Stopping monitoring stack..."
	./scripts/monitoring-setup.sh stop

# Utilities
clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	cd frontend && rm -rf build/ node_modules/ .cache/
	@echo "✅ Cleanup completed"

logs:
	@echo "📋 Showing application logs..."
	docker-compose logs -f

health:
	@echo "🏥 Checking system health..."
	curl -f http://localhost:8000/health || echo "❌ Backend health check failed"
	curl -f http://localhost:3000 || echo "❌ Frontend health check failed"
	curl -f http://localhost:9090/-/healthy || echo "❌ Prometheus health check failed"
	curl -f http://localhost:3001/api/health || echo "❌ Grafana health check failed"

# Security
security-scan:
	@echo "🔒 Running security scans..."
	cd backend && bandit -r app/ -f json -o bandit-report.json
	cd backend && safety check
	docker run --rm -v $(PWD):/app aquasec/trivy fs /app

# Performance
performance-test:
	@echo "⚡ Running performance tests..."
	cd backend && locust -f tests/performance/locustfile.py --headless --users 100 --spawn-rate 10 --run-time 300s

# Documentation
docs:
	@echo "📚 Generating documentation..."
	cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
	sleep 10
	curl http://localhost:8000/openapi.json > docs/api-spec.json
	pkill -f uvicorn

# Quick start for new developers
quickstart: install-dev db-init
	@echo "🚀 Quick start completed!"
	@echo "Run 'make dev' to start development servers"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make lint' to check code quality"
