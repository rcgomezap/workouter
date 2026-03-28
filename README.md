# Workouter

A modern workout tracking platform with GraphQL API, CLI, and end-to-end testing. Built with Python, FastAPI, and Clean Architecture principles.

## Overview

Workouter helps you track your fitness progress through structured mesocycles, routines, and workout sessions. It provides:

- **Mesocycle Management**: Plan multi-week training blocks with progressive overload
- **Routine Templates**: Create reusable workout templates
- **Session Tracking**: Log actual performance (reps, weight, RIR)
- **Bodyweight Tracking**: Monitor your bodyweight progress over time
- **Training Insights**: Volume tracking and progressive overload metrics (e1RM)
- **GraphQL API**: Modern, type-safe API with interactive playground
- **CLI Tool**: Command-line interface optimized for both humans and AI agents

## Monorepo Structure

This repository is organized as a monorepo with three main components:

```
workouter/
├── api/              # Backend GraphQL API
├── cli/              # Command-line interface
├── e2e/              # End-to-end integration tests
└── .github/          # CI/CD workflows
```

### Components

#### [API](./api/README.md)

The backend service powering Workouter, built with FastAPI and Strawberry GraphQL.

**Tech Stack**: Python 3.12+, FastAPI, Strawberry GraphQL, SQLAlchemy 2.0, SQLite, Alembic

**Key Features**:
- Clean Architecture (Domain, Application, Infrastructure, Presentation layers)
- Async-first design with SQLAlchemy 2.0
- Static API key authentication
- Automated database backups
- Comprehensive test suite (unit + integration)

**Quick Start**:
```bash
cd api
make install    # Complete setup (dependencies, hooks, migrations, seed data)
make dev        # Start development server
```

See [api/README.md](./api/README.md) for full documentation.

#### [CLI](./cli/README.md)

A command-line interface for interacting with the Workouter API.

**Tech Stack**: Python 3.14+, Click, gql (GraphQL client), rich (terminal UI)

**Key Features**:
- AI-agent optimized (JSON output, semantic exit codes)
- Hybrid command structure (workflows + full entity access)
- Rich terminal output for humans, clean JSON for agents
- Async GraphQL client
- Comprehensive test coverage (85%+)

**Quick Start**:
```bash
cd cli
uv sync
export WORKOUTER_API_URL=http://localhost:8000/graphql
export WORKOUTER_API_KEY=your-api-key-here
uv run workouter-cli --help
```

See [cli/README.md](./cli/README.md) for full documentation.

#### [E2E Tests](./e2e/)

End-to-end integration tests that verify the complete system (API + CLI).

**Tech Stack**: Python 3.14+, pytest, Docker Compose

**Key Features**:
- Real API server + CLI integration
- Core workflow testing (create, read, update, delete)
- Smoke tests for critical paths
- Dockerized test environment

**Quick Start**:
```bash
cd e2e
uv sync
uv run pytest
```

See [e2e/AGENTS.md](./e2e/AGENTS.md) for full documentation.

## Quick Start (All Components)

### Prerequisites

- **Python**: 3.12+ for API, 3.14+ for CLI and E2E
- **uv**: Fast Python package manager ([installation](https://astral.sh/uv/))
- **Docker** (optional): For containerized deployment

### Setup All Components

```bash
# 1. Install API
cd api
make install
cd ..

# 2. Install CLI
cd cli
uv sync
cd ..

# 3. Install E2E tests
cd e2e
uv sync
cd ..

# 4. Configure API
cd api
cp config.example.yaml config.yaml
# Edit config.yaml to set your api_key
cd ..
```

### Start Development

```bash
# Terminal 1: Start API server
cd api
make dev

# Terminal 2: Use CLI (after API is running)
cd cli
export WORKOUTER_API_URL=http://localhost:8000/graphql
export WORKOUTER_API_KEY=your-api-key-here
uv run workouter-cli --help

# Terminal 3: Run E2E tests (optional)
cd e2e
uv run pytest
```

## Common Development Commands

### API

```bash
cd api
make dev              # Start development server
make test             # Run all tests
make lint             # Check code quality
make format           # Format code
make db-reset         # Reset database (WARNING: deletes all data)
make help             # Show all commands
```

### CLI

```bash
cd cli
make test             # Run all tests
make lint             # Check code quality
make format           # Format code
make type-check       # Run type checker
uv run workouter-cli  # Run CLI
make help             # Show all commands
```

### E2E

```bash
cd e2e
uv run pytest                    # Run all tests
uv run pytest test_smoke.py      # Run smoke tests only
uv run pytest test_core_workflows.py  # Run workflow tests
```

## CI/CD

This project uses GitHub Actions for continuous integration:

- **[API CI](./.github/workflows/api-ci.yml)**: Runs API tests on every PR
- **[API Auto-Format](./.github/workflows/api-auto-format.yml)**: Auto-formats Python code in API
- **[CLI CI](./.github/workflows/cli-ci.yml)**: Runs CLI tests on every PR
- **[E2E CI](./.github/workflows/e2e-ci.yml)**: Runs end-to-end integration tests

All checks must pass before merging to `main`.

## Architecture

This project follows **Clean Architecture** principles across all components:

### Layers

- **Domain**: Core business logic, entities, repository interfaces (no external dependencies)
- **Application**: Use cases, services, DTOs (depends on Domain)
- **Infrastructure**: Database, GraphQL client, external services (implements Domain interfaces)
- **Presentation**: API endpoints, CLI commands, user interface (orchestrates Application)

### Dependency Rule

Inner layers never depend on outer layers. Dependencies point inward:

```
Presentation → Application → Domain ← Infrastructure
```

See component-specific README files for detailed architecture documentation.

## Testing

### Test Strategy

- **Unit Tests**: Test individual components in isolation (≥90% coverage target)
- **Integration Tests**: Test component integration within each service (≥80% coverage)
- **E2E Tests**: Test complete system workflows (core paths covered)

### Running All Tests

```bash
# API tests
cd api && make test

# CLI tests  
cd cli && make test

# E2E tests
cd e2e && uv run pytest
```

## Contributing

### Development Workflow

1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Make your changes** in the appropriate component directory
3. **Write tests** for new functionality
4. **Run checks**: `make lint`, `make format`, `make test` in component directory
5. **Commit with conventional commit messages**:
   - `feat(api):` for new API features
   - `feat(cli):` for new CLI features
   - `fix(api):` for API bug fixes
   - `test(e2e):` for E2E test additions
   - `docs:` for documentation updates
6. **Push and create a pull request**

### PR Requirements

Before submitting a PR, ensure:

- All tests pass in affected components
- Code is formatted (`make format`)
- Linting passes (`make lint`)
- Type checking passes (`make type-check` for CLI)
- PR title follows format: `[Component] Brief description`
  - Examples: `[API] Add bodyweight tracking`, `[CLI] Fix JSON output formatting`

### Pre-commit Hooks

Both API and CLI use pre-commit hooks to ensure code quality:

- **API**: Auto-formats with `ruff format` and runs `ruff check --fix`
- **CLI**: Same as API

Install hooks with `make install` in each component directory.

## Documentation

### Component Documentation

- **[API README](./api/README.md)**: API setup, development, and deployment
- **[API AGENTS.md](./api/AGENTS.md)**: Detailed instructions for AI coding agents
- **[CLI README](./cli/README.md)**: CLI usage, commands, and development
- **[CLI AGENTS.md](./cli/AGENTS.md)**: CLI setup and development for AI agents
- **[CLI DESIGN.md](./cli/DESIGN.md)**: CLI system design and architecture
- **[E2E AGENTS.md](./e2e/AGENTS.md)**: E2E test setup and execution

### API Documentation

- **GraphQL Playground**: Visit `http://localhost:8000/graphql` (when `server.debug` is true)
- **OpenAPI/Swagger**: `http://localhost:8000/docs`
- **Health Check**: `GET http://localhost:8000/health`
- **Schema Export**: `cd api && make schema` generates `schema.graphql`

## Deployment

### Docker

Each component can be built and deployed with Docker:

```bash
# API
cd api
make docker-up      # Start with Docker Compose
make docker-down    # Stop containers

# CLI
cd cli
docker build -t workouter-cli .
docker run --rm \
  -e WORKOUTER_API_URL=http://api:8000/graphql \
  -e WORKOUTER_API_KEY=your-key \
  workouter-cli exercises list --json
```

### Production Considerations

- **API**: Set `server.debug: false` in `config.yaml`
- **Authentication**: Use strong API keys (generate with `secrets.token_urlsafe(32)`)
- **Database**: Consider PostgreSQL for production (currently SQLite)
- **Backups**: Configure automated backups in API config
- **Logging**: Use structured JSON logging for production monitoring

## Support and Issues

- **Bug Reports**: [Open an issue](https://github.com/rcgomezap/workouter/issues/new?labels=bug)
- **Feature Requests**: [Open an issue](https://github.com/rcgomezap/workouter/issues/new?labels=enhancement)
- **Discussions**: Use GitHub Discussions for questions and ideas

## License

[Your License Here]

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Strawberry GraphQL](https://strawberry.rocks/) - Python GraphQL library
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
- [Click](https://click.palletsprojects.com/) - CLI framework
- [uv](https://astral.sh/uv/) - Fast Python package manager
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
