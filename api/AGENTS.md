# AGENTS.md

## Project Overview

Workout Tracker API is a backend service for tracking fitness progress, including mesocycles, routines, sessions, and exercises. It features GraphQL API, bodyweight tracking, and progressive overload insights.

- **Tech Stack**: Python 3.12+, FastAPI, Strawberry GraphQL, SQLAlchemy 2.0 (async), SQLite (aiosqlite), Alembic, Pydantic v2, structlog, APScheduler.
- **Architecture**: Clean Architecture (Presentation, Application, Domain, Infrastructure layers).
- **Package Manager**: `uv`.

## Setup Commands

### Quick Setup (Recommended)
- **Complete setup**: `make install` (installs dependencies, pre-commit hooks, runs migrations, seeds data)
- **Start development**: `make dev`
- **View all commands**: `make help`

### Manual Setup (Alternative)
- Install `uv` if not present: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Install dependencies: `uv sync`
- Install pre-commit hooks: `uv run pre-commit install`
- Initialize config: `cp config.example.yaml config.yaml` (Update `api_key` and other settings)
- Run database migrations: `PYTHONPATH=src uv run alembic upgrade head`
- Seed initial data (Muscle Groups): `PYTHONPATH=src uv run python -m app.infrastructure.seed`

## Development Workflow

- **Start development server**: `make dev` or `uv run uvicorn app.main:create_app --factory --reload`
- **Run tests**: `make test` or `uv run pytest`
- **Lint code**: `make lint` or `uv run ruff check .`
- **Format code**: `make format` or `uv run ruff format .`
- **Type check**: `make type-check` or `uv run mypy src`
- **Export GraphQL Schema**: `make schema` or `PYTHONPATH=src uv run python src/export_schema.py > schema.graphql`
- **Reset database**: `make db-reset` (WARNING: deletes all data)
- **Check logs**: Structured JSON logs are output to stdout or configured file.
- **Database**: Defaults to `data/workout_tracker.db` (SQLite). Use `sqlite3` or similar for manual inspection.

## Testing Instructions

- **Quick Commands**:
  - `make test` - Run all tests
  - `make test-unit` - Run unit tests only
  - `make test-integration` - Run integration tests only
  - `make test-cov` - Run with coverage report
  - `make test-quick` - Optimized for minimal output (CI-friendly)

- **Manual Commands**:
  - `uv run pytest` - Run all tests
  - `uv run pytest tests/unit` - Unit tests only
  - `uv run pytest tests/integration` - Integration tests only
  - `uv run pytest --cov=app --cov-report=term-missing` - With coverage
  - `uv run pytest -q --tb=short --disable-warnings` - Minimal output (recommended for agents)

- **Note**: Integration tests use an in-memory SQLite database.
- **Important**: If tests do not pass, ALWAYS debug them individually (e.g., `uv run pytest tests/integration/test_file.py -k test_name -vv`) to avoid filling up the context window.
- **Subagent Assignment**: For complex or multiple test failures, ALWAYS assign a specialized subagent (e.g., `explore` or `general`) to perform deep-dive debugging. The subagent must return a detailed analysis of the root cause and recommended fixes to the main agent.

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

- **Build Docker image**: `make build` or `docker build -t workout-tracker .`
- **Run with Docker Compose**: `make docker-up` or `docker compose up`
- **Stop Docker services**: `make docker-down` or `docker compose down`
- The Dockerfile uses a multi-stage build (base, test, production). Build will fail if tests do not pass.

## PR Instructions

Before submitting a PR, ensure:
- All tests pass: `make test` or `uv run pytest`
- Linting passes: `make lint` or `uv run ruff check .`
- Code is formatted: `make format` or `uv run ruff format .`
- Types are valid: `make type-check` or `uv run mypy src`
- Title format: `[Component] Brief description of change`

**Note**: Pre-commit hooks will automatically run `ruff format` and `ruff check --fix` on staged files before each commit.

## Additional Notes

- **Authentication**: All GraphQL requests require `Authorization: Bearer <api_key>` header.
- **Timestamps**: All timestamps must be UTC (`datetime.now(UTC)`).
- **Backups**: Trigger manual backup via `triggerBackup` GraphQL mutation. Backups are stored in the `backups/` directory.
- **GraphQL Convention**: snake_case for Python code, camelCase for GraphQL fields (Strawberry naming convention).

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The hooks are automatically installed when running `make install`.

**Manual installation**: `uv run pre-commit install`

**What the hooks do**:
- Run `ruff check --fix` to automatically fix linting issues
- Run `ruff format` to format code

**Note**: Commits will be blocked if there are unfixable linting errors. Fix them before committing.
