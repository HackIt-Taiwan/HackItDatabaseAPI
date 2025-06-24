.PHONY: help build start stop restart logs clean test install dev

# Default target
help: ## Show this help message
	@echo "HackIt Database Service Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker containers
	docker-compose build

start: ## Start all services
	docker-compose up -d

stop: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View logs
	docker-compose logs -f

logs-db: ## View database service logs
	docker-compose logs -f database-service

logs-mongo: ## View MongoDB logs
	docker-compose logs -f mongo

clean: ## Remove containers and volumes
	docker-compose down -v
	docker system prune -f

test: ## Run health checks
	@echo "Testing database service..."
	@curl -f http://localhost:8001/health || echo "Service not available"

install: ## Install dependencies for local development
	cd database-service && pip install -r requirements.txt
	cd database-client && pip install -r requirements.txt

dev: ## Start in development mode
	cd database-service && python main.py

dev-service: ## Start database service only
	docker-compose up -d mongo redis
	cd database-service && python main.py

setup: ## Initial setup
	cp .env.example .env
	@echo "Please edit .env file with your configuration"

docker-build: ## Build Docker image for production
	docker build -t hackit-database-service:latest ./database-service

docker-run: ## Run Docker container
	docker run -p 8001:8001 --env-file .env hackit-database-service:latest

# Development shortcuts
mongo-shell: ## Connect to MongoDB shell
	docker-compose exec mongo mongosh hackit_db

redis-cli: ## Connect to Redis CLI
	docker-compose exec redis redis-cli

status: ## Check service status
	@echo "Checking service status..."
	@docker-compose ps
	@echo ""
	@echo "Health checks:"
	@curl -s http://localhost:8001/health | jq . || echo "Database service not available" 