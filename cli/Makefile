.PHONY: help install dev test test-unit test-integration test-cov test-quick lint format type-check build clean docker-build docker-run

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and setup
	@echo "Installing dependencies..."
	uv sync
	@echo "✓ Installation complete"

dev: ## Run CLI in development mode
	@echo "Running workouter-cli..."
	uv run workouter-cli --help

test: ## Run all tests
	@echo "Running all tests..."
	uv run pytest tests/ -v

test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	uv run pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "Running integration tests..."
	uv run pytest tests/integration/ -v

test-cov: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	uv run pytest --cov=workouter_cli --cov-report=term-missing --cov-report=html

test-quick: ## Run tests with minimal output (CI-friendly)
	@echo "Running tests (minimal output)..."
	uv run pytest -q --tb=short --disable-warnings

lint: ## Run linter (ruff check)
	@echo "Running linter..."
	uv run ruff check .

lint-fix: ## Run linter with auto-fix
	@echo "Running linter with auto-fix..."
	uv run ruff check --fix .

format: ## Format code (ruff format)
	@echo "Formatting code..."
	uv run ruff format .

type-check: ## Run type checker (mypy)
	@echo "Running type checker..."
	uv run mypy src

build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t workouter-cli .
	@echo "✓ Docker image built: workouter-cli"

docker-run: ## Run CLI in Docker (requires env vars)
	@echo "Running CLI in Docker..."
	docker run --rm \
		-e WORKOUTER_API_URL=${WORKOUTER_API_URL} \
		-e WORKOUTER_API_KEY=${WORKOUTER_API_KEY} \
		workouter-cli --help

clean: ## Remove cache and build artifacts
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup complete"

all: lint format type-check test ## Run all checks (lint, format, type-check, test)
	@echo "✓ All checks passed"
