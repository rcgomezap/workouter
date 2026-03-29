# Workout Tracker API

A modern Workout Tracker API built with Python, FastAPI, Strawberry GraphQL, and SQLAlchemy.

## Features

- **Mesocycle Management**: Plan multi-week training blocks.
- **Routine Templates**: Create reusable workout templates with exercises and sets.
- **Session Tracking**: Log actual performance (reps, weight, RIR) for workout sessions.
- **GraphQL API**: Code-first schema with Strawberry.
- **Security**: Static API key authentication.
- **Insights**: Volume tracking and progressive overload (e.g., e1RM) insights.
- **Backup System**: Automated and manual SQLite database backups.
- **Migrations**: Database schema versioning with Alembic.

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://astral.sh/uv/) (recommended) or pip

### Local Setup

#### Option 1: Using Makefile (Recommended)

1. **Complete setup**:
   ```bash
   make install
   ```
   This will:
   - Install all dependencies
   - Set up pre-commit hooks for code quality
   - Create `config.yaml` from template (if it doesn't exist)
   - Run database migrations
   - Seed initial data

2. **Configure** (if first time):
   ```bash
   # Edit config.yaml to set your api_key
   nano config.yaml  # or your preferred editor
   ```

3. **Start Server**:
   ```bash
   make dev
   ```

#### Option 2: Manual Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

3. **Configure**:
   ```bash
   cp config.example.yaml config.yaml
   # Edit config.yaml to set your api_key and other settings
   ```

4. **Run Migrations**:
   ```bash
   PYTHONPATH=src uv run alembic upgrade head
   ```

5. **Seed Data**:
   ```bash
   PYTHONPATH=src uv run python -m app.infrastructure.seed
   ```

6. **Start Server**:
   ```bash
   PYTHONPATH=src uv run uvicorn app.main:create_app --factory --reload
   ```

The API will be available at `http://localhost:8000`. Access GraphQL at `http://localhost:8000/graphql`.

### Common Commands

View all available commands:
```bash
make help
```

Key commands:
- `make dev` - Start development server
- `make test` - Run all tests
- `make lint` - Check code quality
- `make format` - Format code
- `make db-reset` - Reset database (deletes all data!)

### Docker

```bash
make docker-up    # or: docker compose up --build
make docker-down  # or: docker compose down
```

### DockerHub Image

Release tags (`v*`) publish a multi-arch API image to DockerHub with the same shared
version as the CLI.

```bash
# Stable tag for a release
docker pull <dockerhub-username>/workouter-api:0.1.3

# Latest release
docker pull <dockerhub-username>/workouter-api:latest
```

Supported platforms:
- `linux/amd64`
- `linux/arm64`

To run the published image with your local config/data volumes:

```bash
docker run --rm -p 8000:8000 \
  -e CONFIG_PATH=/app/config.yaml \
  -v "$(pwd)/config.yaml:/app/config.yaml" \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/backups:/app/backups" \
  <dockerhub-username>/workouter-api:latest
```

## Documentation

- **GraphQL API**: Visit `/graphql` for the interactive playground (when `server.debug` is true).
- **Export Schema**: To generate a `schema.graphql` file for tools like Postman:
  ```bash
  PYTHONPATH=src uv run python src/export_schema.py > schema.graphql
  ```
- **REST Health Check**: `GET /health`
- **OpenAPI/Swagger**: `GET /docs`

## Testing

```bash
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make test-cov          # Run with coverage report
make test-quick        # Quick run for CI (minimal output)
```

Manual alternative:
```bash
uv run pytest
```

## Architecture

This project follows **Clean Architecture** principles:
- `domain/`: Core business logic, entities, and repository interfaces.
- `application/`: Use cases, services, and DTOs.
- `infrastructure/`: Database models, repository implementations, and external services.
- `presentation/`: GraphQL schema, resolvers, and API middleware.
