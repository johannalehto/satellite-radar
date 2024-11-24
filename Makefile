
APP_NAME := satellite_catalog_api
DOCKER_COMPOSE := docker-compose
POETRY := poetry
PYTHON := python

# Docker
.PHONY: start down build docker-logs
start:  ## Start Docker containers in detached mode
	$(DOCKER_COMPOSE) up -d

down:  ## Stop and remove Docker containers and orphans
	$(DOCKER_COMPOSE) down --remove-orphans

build:  ## Build Docker images
	$(DOCKER_COMPOSE) build

docker-logs:  ## View Docker logs
	$(DOCKER_COMPOSE) logs -f

script: ## Run a script in the app container
	$(DOCKER_COMPOSE) exec app poetry run python scripts/$(script)

# Local development
.PHONY: run-local
run-local:  ## Run the app locally with Poetry
	$(POETRY) run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing and　formatting
.PHONY: test format lint
test:  ## Run all tests with pytest
	$(POETRY) run pytest --color=yes -s -vvv --log-cli-level=INFO

format:  ## Format code with black, isort, and run flake8
	$(POETRY) run black .
	$(POETRY) run isort .
	$(POETRY) run flake8 .

lint:  ## Run pre-commit hooks for linting
	$(POETRY) run pre-commit run --all-files

# Dependency management
.PHONY: install update-dependencies
install:  ## Install dependencies with Poetry
	$(POETRY) install

update-dependencies:  ## Update dependencies with Poetry
	$(POETRY) update

# Celery Tasks
.PHONY: celery-worker celery-beat
celery-worker:  ## Start Celery worker
	$(POETRY) run celery -A app.satellite_catalog.celery worker --loglevel=info

celery-beat:  ## Start Celery beat scheduler
	$(POETRY) run celery -A app.satellite_catalog.celery beat --loglevel=info

# Help
.PHONY: help
help:  ## Display help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
