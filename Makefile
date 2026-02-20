
APP_NAME := satellite_catalog_api
DOCKER_COMPOSE := docker-compose
DOCKER_EXEC := docker exec -it
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

# eg. make script name=update_satellite_catalog.py
script: ## Run a script in the app container
	$(DOCKER_COMPOSE) exec app poetry run python scripts/$(name)

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

# Celery tasks
.PHONY: celery-worker celery-beat docker-celery-worker
celery-worker:  ## start Celery worker
	$(POETRY) run celery -A app.satellite_catalog.celery_app worker --loglevel=info

celery-beat:  ## start Celery beat scheduler
	$(POETRY) run celery -A app.satellite_catalog.celery_app beat --loglevel=info

docker-celery-worker:  ## start Celery worker in Docker container
	$(DOCKER_EXEC) celery_worker poetry run celery -A app.satellite_catalog.celery_app worker --loglevel=info

run-celery-task:  ## start Celery worker & trigger the task
	docker exec -it celery_worker poetry run celery -A app.satellite_catalog.celery_app call app.satellite_catalog.tasks.scheduled_update

#  Satellite catalog updater
deploy-scheduled-updater:
	@echo "🔪 Cleaning old stopped machines..."
	fly machines list -a satellite-catalog-updater --json | \
	jq -r '.[] | select(.state == "stopped") | .id' | \
	xargs -r -n1 fly machine destroy -a satellite-catalog-updater

	@echo "🚀 Deploying latest code..."
	fly deploy -c fly.updater.toml --no-cache

	@echo "📆 Creating new scheduled daily machine (12:00 JST)..."
	fly machine run . -a satellite-catalog-updater  \
		--schedule daily \
		--restart no \
		--region arn \
		--vm-size shared-cpu-1x \
		--memory 256 \
		python app/satellite_catalog/run_updater.py



# Help
.PHONY: help
help:  ## Display help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
