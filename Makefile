.PHONY: help build up down restart logs test clean init-db migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	docker compose -f docker-compose.dev.yml build

up: ## Start services in development mode
	docker compose -f docker-compose.dev.yml up -d

down: ## Stop services
	docker compose -f docker-compose.dev.yml down

restart: ## Restart services
	docker compose -f docker-compose.dev.yml restart

logs: ## Show logs
	docker compose -f docker-compose.dev.yml logs -f web

test: ## Run tests
	docker compose -f docker-compose.dev.yml exec web pytest

test-local: ## Run tests locally
	pytest

init-db: ## Initialize database
	docker compose -f docker-compose.dev.yml exec web flask init-db

seed-datasets: ## Seed sample datasets (medallion architecture)
	docker compose -f docker-compose.dev.yml exec web flask seed-datasets

seed-datasets-local: ## Seed datasets locally (without Docker)
	flask seed-datasets

migrate: ## Create database migration (usage: make migrate MESSAGE="description")
	docker compose -f docker-compose.dev.yml exec web flask db migrate -m "$(MESSAGE)"

upgrade: ## Apply database migrations
	docker compose -f docker-compose.dev.yml exec web flask db upgrade

shell: ## Open Python shell in container
	docker compose -f docker-compose.dev.yml exec web flask shell

clean: ## Remove containers and volumes
	docker compose -f docker-compose.dev.yml down -v
	docker system prune -f


