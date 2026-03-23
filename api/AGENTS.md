# AGENTS.md

## Project Overview

Workout Tracker API is a backend service for tracking fitness progress, including mesocycles, routines, sessions, and exercises. It features GraphQL API, bodyweight tracking, and progressive overload insights.

- **Tech Stack**: Python 3.12+, FastAPI, Strawberry GraphQL, SQLAlchemy 2.0 (async), SQLite (aiosqlite), Alembic, Pydantic v2, structlog, APScheduler.
- **Architecture**: Clean Architecture (Presentation, Application, Domain, Infrastructure layers).
- **Package Manager**: `uv`.

## Setup Commands

- Install `uv` if not present: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Install dependencies: `uv sync`
- Initialize config: `cp config.example.yaml config.yaml` (Update `api_key` and other settings)
- Run database migrations: `uv run alembic upgrade head`
- Seed initial data (Muscle Groups): `uv run python -m app.infrastructure.seed` (Note: ensure you are in `src` or have it in PYTHONPATH)

## Development Workflow

- Start development server: `uv run uvicorn app.main:create_app --factory --reload`
- Check logs: Structured JSON logs are output to stdout or configured file.
- Database: Defaults to `data/workout_tracker.db` (SQLite). Use `sqlite3` or similar for manual inspection.
- Linting and Formatting: `uv run ruff check .` and `uv run ruff format .`

## Testing Instructions

- Run all tests: `uv run pytest`
- Run unit tests: `uv run pytest tests/unit`
- Run integration tests: `uv run pytest tests/integration`
- Test coverage: `uv run pytest --cov=app --cov-report=term-missing`
- Note: Integration tests use an in-memory SQLite database.
- Important: If tests do not pass, ALWAYS debug them individually to avoid filling up the context window.

## Code Style

- **Conventions**: PEP 8, absolute imports starting with `app.`.
- **Async**: Use `async`/`await` for all I/O, including database and resolvers.
- **Typing**: 100% type hint coverage. Use `|` for unions and `list[]`/`dict[]` for collections.
- **Layers**: 
    - `domain/`: Entities (dataclasses), Enums, Repository Interfaces.
    - `application/`: Services, DTOs, Unit of Work interface.
    - `infrastructure/`: SQLAlchemy models, Repository implementations, UoW implementation.
    - `presentation/`: GraphQL schema, Resolvers, Middleware.

## Build and Deployment

- Build Docker image: `docker build -t workout-tracker .`
- Run with Docker Compose: `docker compose up`
- The Dockerfile uses a multi-stage build (base, test, production). Build will fail if tests do not pass.

## PR Instructions

- Ensure all tests pass: `uv run pytest`
- Ensure linting passes: `uv run ruff check .`
- Ensure types are valid: `uv run mypy src`
- Title format: `[Component] Brief description of change`

## Additional Notes

- **Authentication**: All GraphQL requests require `Authorization: Bearer <api_key>` header.
- **Timestamps**: All timestamps must be UTC (`datetime.now(UTC)`).
- **Backups**: Trigger manual backup via `triggerBackup` GraphQL mutation. Backups are stored in the `backups/` directory.
- **GraphQL Convention**: snake_case for Python code, camelCase for GraphQL fields (Strawberry naming convention).
