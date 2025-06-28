# FII Scraper API - Makefile
.PHONY: help install format test docker-build docker-clean
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)FII Scraper API Commands$(NC)"
	@echo "========================="
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

## Development Commands
install: ## Install dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	poetry install

format: ## Format code with black, isort, and autoflake
	@echo "$(BLUE)🎨 Formatting code...$(NC)"
	poetry run black .
	poetry run isort .
	poetry run autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive -v .

test: ## Run unit tests
	@echo "$(BLUE)🧪 Running unit tests...$(NC)"
	poetry run pytest tests/unit/ -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(NC)"
	poetry run pytest tests/unit/ -v

test-integration: ## Run integration tests with DynamoDB
	@echo "$(BLUE)🧪 Running integration tests...$(NC)"
	@echo "$(YELLOW)📦 Starting DynamoDB for integration tests...$(NC)"
	docker-compose --profile integration up -d dynamodb-local
	@echo "$(YELLOW)⏳ Waiting for DynamoDB to initialize...$(NC)"
	@sleep 5
	@echo "$(GREEN)✅ DynamoDB should be ready!$(NC)"
	poetry run pytest tests/integration/ -v
	@echo "$(BLUE)🛑 Stopping DynamoDB...$(NC)"
	docker-compose --profile integration down

test-e2e: ## Run E2E tests with full application
	@echo "$(BLUE)🧪 Running E2E tests...$(NC)"
	@echo "$(YELLOW)📦 Starting application and DynamoDB for E2E tests...$(NC)"
	docker-compose --profile e2e up -d --build
	@echo "$(YELLOW)⏳ Waiting for application to be ready...$(NC)"
	@timeout 60 bash -c 'until curl -sf http://localhost:8080/health > /dev/null 2>&1; do sleep 3; done' || (echo "$(RED)❌ Application failed to start$(NC)" && docker-compose --profile e2e logs && exit 1)
	@echo "$(GREEN)✅ Application is ready!$(NC)"
	poetry run pytest tests/e2e/ -v
	@echo "$(BLUE)🛑 Stopping test environment...$(NC)"
	docker-compose --profile e2e down

test-all: test-unit test-integration test-e2e ## Run all tests (unit, integration, e2e)

run-local: ## Run API locally with Poetry
	@echo "$(BLUE)🚀 Starting API locally...$(NC)"
	export FII_REPOSITORY_TYPE=dynamodb && poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001

## Docker Commands
docker-build: ## Build Docker images
	@echo "$(BLUE)🐳 Building Docker images...$(NC)"
	docker-compose build

docker-clean: ## Clean Docker containers and images
	@echo "$(BLUE)🧹 Cleaning Docker containers...$(NC)"
	docker-compose down -v
	docker system prune -f

## Development Environment
dev-up: ## Start development environment (API + DynamoDB)
	@echo "$(BLUE)🚀 Starting development environment...$(NC)"
	docker-compose --profile dev up --build -d
	@echo "$(GREEN)✅ Development environment started!$(NC)"
	@echo "$(YELLOW)📡 API: http://localhost:8001$(NC)"
	@echo "$(YELLOW)📚 Docs (ReDoc): http://localhost:8001/docs$(NC)"
	@echo "$(YELLOW)🗄️ DynamoDB: http://localhost:8002$(NC)"

dev-down: ## Stop development environment
	@echo "$(BLUE)🛑 Stopping development environment...$(NC)"
	docker-compose down

dev-logs: ## Show development logs
	@echo "$(BLUE)📋 Showing development logs...$(NC)"
	docker-compose logs -f fii-scraper-dev

dev-restart: ## Restart development environment
	@echo "$(BLUE)🔄 Restarting development environment...$(NC)"
	docker-compose restart fii-scraper-dev

## Production Environment
prod-up: ## Start production environment
	@echo "$(BLUE)🚀 Starting production environment...$(NC)"
	docker-compose up fii-scraper --build -d
	@echo "$(GREEN)✅ Production environment started!$(NC)"
	@echo "$(YELLOW)📡 API: http://localhost:8000$(NC)"

prod-down: ## Stop production environment
	@echo "$(BLUE)🛑 Stopping production environment...$(NC)"
	docker-compose down

prod-logs: ## Show production logs
	@echo "$(BLUE)📋 Showing production logs...$(NC)"
	docker-compose logs -f fii-scraper

## API Testing & Health
health: ## Check API health
	@echo "$(BLUE)🏥 Checking API health...$(NC)"
	@sleep 2
	@curl -s http://localhost:8001/health || echo "$(RED)❌ API not responding$(NC)"

status: ## Check database status
	@echo "$(BLUE)📊 Checking database status...$(NC)"
	@sleep 2
	@curl -s http://localhost:8001/database/status || echo "$(RED)❌ API not responding$(NC)"

docs: ## Open API documentation (ReDoc)
	@echo "$(BLUE)📚 Opening API documentation...$(NC)"
	@echo "$(YELLOW)🌐 ReDoc: http://localhost:8001/docs$(NC)"
	@python3 -m webbrowser http://localhost:8001/docs 2>/dev/null || echo "$(YELLOW)💡 Open http://localhost:8001/docs in your browser$(NC)"

## Full Workflow
dev-full: dev-clean dev-up wait-for-api test-e2e ## Full development setup
	@echo "$(GREEN)🎉 Full development environment ready!$(NC)"

wait-for-api: ## Wait for API to be ready
	@echo "$(BLUE)⏳ Waiting for API to be ready...$(NC)"
	@timeout 60 bash -c 'until curl -sf http://localhost:8001/health > /dev/null; do sleep 2; done' || (echo "$(RED)❌ API failed to start$(NC)" && exit 1)
	@echo "$(GREEN)✅ API is ready!$(NC)"

dev-clean: dev-down docker-clean ## Clean everything and start fresh

## Monitoring
monitor: ## Show real-time container status
	@echo "$(BLUE)📊 Container Status:$(NC)"
	@docker-compose ps

tail-logs: ## Tail all logs
	@docker-compose logs -f

## Quick Commands
quick-test: dev-up wait-for-api test-e2e dev-down ## Quick test cycle
