
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

# Testing and formatting
.PHONY: test format lint

test:  ## Run tests with coverage (verbose)
	$(POETRY) run pytest \
		--color=yes \
		-s \
		-vvv \
		--log-cli-level=INFO \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=xml

format:  ## Auto-fix lint issues and format code
	$(POETRY) run ruff check . --fix
	$(POETRY) run black .

lint:  ## Check linting and formatting (CI-safe)
	$(POETRY) run ruff check .
	$(POETRY) run black --check .

# Dependency management
.PHONY: install update-dependencies
install:  ## Install dependencies with Poetry
	$(POETRY) install

update-dependencies:  ## Update dependencies with Poetry
	$(POETRY) update

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
		python app/satellite_catalog/updater.py



# Help
.PHONY: help
help:  ## Display help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
