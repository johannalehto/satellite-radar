
APP_NAME := satellite_catalog_api
DOCKER_COMPOSE := docker-compose
DOCKER_EXEC := docker exec -it
POETRY := poetry
PYTHON := python

# Docker
.PHONY: start down build docker-logs update-catalog-local
start:  ## Start Docker containers in detached mode
	$(DOCKER_COMPOSE) up -d

down:  ## Stop and remove Docker containers and orphans
	$(DOCKER_COMPOSE) down --remove-orphans

build:  ## Build Docker images
	$(DOCKER_COMPOSE) build

docker-logs:  ## View Docker logs
	$(DOCKER_COMPOSE) logs -f

update-catalog-local:  ## Populate the local Docker Mongo catalog from CelesTrak
	$(DOCKER_COMPOSE) exec app python -m app.satellite_catalog.updater

# eg. make script name=update_satellite_catalog.py
script: ## Run a script in the app container
	$(DOCKER_COMPOSE) exec app poetry run python scripts/$(name)

# Local development
.PHONY: run-local run-debug-ui
run-local:  ## Run the app locally with Poetry
	$(POETRY) run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-debug-ui:  ## Serve the debug UI locally on port 3000
	$(PYTHON) -m http.server 3000 --directory debug

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

# Deployment
.PHONY: deploy-api deploy-debug-ui deploy-scheduled-updater
deploy-api:  ## Deploy the FastAPI app to Fly
	flyctl deploy --remote-only -a satellite-radar -c fly.api.toml

deploy-debug-ui:  ## Deploy the debug UI to Fly
	flyctl deploy --remote-only -a satellites-debug-ui -c debug/fly.toml debug

deploy-scheduled-updater:  ## Recreate the scheduled catalog updater Fly Machine
	@echo "📋 Listing old machines..."
	OLD_IDS="$$(fly machines list -a satellite-catalog-updater --json | python3 -c "import sys, json; print(' '.join(m['id'] for m in json.load(sys.stdin)))")"; \
	echo "Old machines: $${OLD_IDS:-<none>}"; \
	echo "🚀 Creating new scheduled machine..."; \
	fly machine run . -a satellite-catalog-updater \
		--schedule daily \
		--restart no \
		--region arn \
		--vm-size shared-cpu-1x \
		--memory 256 \
		-- \
		python -m app.satellite_catalog.updater; \
	echo "🧹 Destroying old machines..."; \
	for id in $$OLD_IDS; do \
		echo "Destroying machine $$id"; \
		fly machine destroy "$$id" -a satellite-catalog-updater --force || echo "Skipping destroy failure for $$id"; \
	done



# Help
.PHONY: help
help:  ## Display help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
