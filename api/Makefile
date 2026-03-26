.PHONY: help install build run dev test test-unit test-integration test-cov test-quick lint format format-check type-check schema docker-up docker-down db-reset clean

.DEFAULT_GOAL := help

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36mmake %-18s\033[0m %s\n", $$1, $$2}'

install:  ## Complete project setup (dependencies + hooks + migrations + seed)
	@echo "Installing dependencies..."
	uv sync
	@echo "Installing pre-commit hooks..."
	uv run pre-commit install
	@echo "Creating config.yaml if it doesn't exist..."
	@if [ ! -f config.yaml ]; then \
		cp config.example.yaml config.yaml && \
		echo "✓ Created config.yaml from template. Please update the api_key!"; \
	else \
		echo "✓ config.yaml already exists, skipping..."; \
	fi
	@echo "Running database migrations..."
	PYTHONPATH=src uv run alembic upgrade head
	@echo "Seeding initial data (muscle groups)..."
	PYTHONPATH=src uv run python -m app.infrastructure.seed
	@echo ""
	@echo "✓ Setup complete! Next steps:"
	@echo "  1. Edit config.yaml to set your API key"
	@echo "  2. Run 'make dev' to start the development server"

build:  ## Build Docker image
	docker build -t workout-tracker:latest .

run:  ## Run development server with auto-reload
	PYTHONPATH=src uv run uvicorn app.main:create_app --factory --reload

dev: run  ## Alias for run (start development server)

test:  ## Run all tests
	uv run pytest

test-unit:  ## Run unit tests only
	uv run pytest tests/unit

test-integration:  ## Run integration tests only
	uv run pytest tests/integration

test-cov:  ## Run tests with coverage report
	uv run pytest --cov=app --cov-report=term-missing

test-quick:  ## Run tests with minimal output (optimized for CI)
	uv run pytest -q --tb=short --disable-warnings

lint:  ## Run ruff linting checks
	uv run ruff check .

format:  ## Format code with ruff
	uv run ruff format .

format-check:  ## Check if code is formatted (CI-friendly)
	uv run ruff format --check .

type-check:  ## Run mypy type checking
	uv run mypy src

schema:  ## Export GraphQL schema to schema.graphql
	PYTHONPATH=src uv run python src/export_schema.py > schema.graphql
	@echo "✓ Schema exported to schema.graphql"

docker-up:  ## Start services with docker-compose
	docker compose up --build

docker-down:  ## Stop docker-compose services
	docker compose down

db-reset:  ## Reset database (WARNING: deletes all data!)
	@echo "⚠️  WARNING: This will delete all database data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f data/workout_tracker.db; \
		echo "Removed database file"; \
		PYTHONPATH=src uv run alembic upgrade head; \
		echo "Recreated database schema"; \
		PYTHONPATH=src uv run python -m app.infrastructure.seed; \
		echo "✓ Database reset complete"; \
	else \
		echo "Cancelled"; \
	fi

clean:  ## Remove build artifacts, cache, and temporary files
	@echo "Cleaning up..."
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleanup complete"
