.PHONY: help install dev test test-unit test-integration test-cov test-quick lint lint-fix format type-check build binary binary-onedir binary-smoke appimage binary-clean clean docker-build docker-run all

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
	uv run pytest --cov=workouter_cli --cov-report=term-missing --cov-report=html --cov-fail-under=85

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

binary: ## Build one-file executable via PyInstaller
	@echo "Building binary..."
	uv run pyinstaller --onefile --name workouter-cli src/workouter_cli/main.py
	@echo "✓ Binary built: dist/workouter-cli"

binary-onedir: ## Build one-dir executable bundle via PyInstaller
	@echo "Building one-dir bundle..."
	uv run pyinstaller --onedir --name workouter-cli src/workouter_cli/main.py
	@echo "✓ Bundle built: dist/workouter-cli/"

binary-smoke: binary ## Run binary smoke test
	@echo "Running binary smoke test..."
	@version_output="$$(./dist/workouter-cli --version)"; \
	if [ -z "$$version_output" ]; then \
		echo "✗ Binary produced empty --version output"; \
		exit 1; \
	fi; \
	echo "$$version_output"

binary-clean: ## Remove PyInstaller artifacts
	@echo "Cleaning binary artifacts..."
	rm -rf build dist *.spec
	@echo "✓ Binary artifacts removed"

appimage: binary-onedir ## Build Linux AppImage from one-dir bundle
	@echo "Building AppImage..."
	rm -rf AppDir
	mkdir -p AppDir/usr/bin
	cp -R dist/workouter-cli/. AppDir/usr/bin/
	printf '%s\n' '#!/bin/sh' 'HERE=$$(dirname "$$(readlink -f "$$0")")' 'exec "$$HERE/usr/bin/workouter-cli" "$$@"' > AppDir/AppRun
	chmod +x AppDir/AppRun
	printf '%s\n' '[Desktop Entry]' 'Type=Application' 'Name=Workouter CLI' 'Exec=workouter-cli --help' 'Icon=workouter-cli' 'Categories=Utility;' 'Terminal=true' > AppDir/workouter-cli.desktop
	printf '%s\n' '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256"><rect width="256" height="256" rx="48" fill="#111827"/><text x="50%" y="56%" dominant-baseline="middle" text-anchor="middle" fill="#f9fafb" font-family="monospace" font-size="72" font-weight="700">WO</text></svg>' > AppDir/workouter-cli.svg
	ln -sf workouter-cli.svg AppDir/.DirIcon
	if [ ! -x ./appimagetool-x86_64.AppImage ]; then curl -sSL -o appimagetool-x86_64.AppImage https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage; chmod +x appimagetool-x86_64.AppImage; fi
	ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 ./appimagetool-x86_64.AppImage AppDir dist/workouter-cli-linux-x86_64.AppImage
	rm -rf AppDir build dist/workouter-cli *.spec
	@echo "✓ AppImage built: dist/workouter-cli-linux-x86_64.AppImage"

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
	find . -type f -name "*.spec" -delete 2>/dev/null || true
	@echo "✓ Cleanup complete"

all: lint format type-check test ## Run all checks (lint, format, type-check, test)
	@echo "✓ All checks passed"
