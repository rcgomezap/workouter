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

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure**:
   ```bash
   cp config.example.yaml config.yaml
   # Edit config.yaml to set your api_key and other settings
   ```

3. **Run Migrations**:
   ```bash
   PYTHONPATH=src uv run alembic upgrade head
   ```

4. **Seed Data**:
   ```bash
   PYTHONPATH=src uv run python -m app.infrastructure.seed
   ```

5. **Start Server**:
   ```bash
   PYTHONPATH=src uv run uvicorn app.main:create_app --factory --reload
   ```

The API will be available at `http://localhost:8000`. Access GraphQL at `http://localhost:8000/graphql`.

### Docker

```bash
docker-compose up --build
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
uv run pytest
```

## Architecture

This project follows **Clean Architecture** principles:
- `domain/`: Core business logic, entities, and repository interfaces.
- `application/`: Use cases, services, and DTOs.
- `infrastructure/`: Database models, repository implementations, and external services.
- `presentation/`: GraphQL schema, resolvers, and API middleware.
