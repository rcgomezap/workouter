# AGENTS.md

## Project Overview

Workouter CLI is a command-line interface for the Workouter API, designed for both human users and AI agents. It provides a hybrid command structure with workflow-based shortcuts for common tasks and full GraphQL entity access for advanced operations. Built with Python 3.14+, Click framework, and gql GraphQL client, following clean architecture principles.

- **Tech Stack**: Python 3.14+, Click 8.1+, gql 3.5+ (GraphQL client), rich (table rendering), httpx (HTTP client), Pydantic v2 (validation), structlog (logging)
- **Architecture**: Clean Architecture (Presentation → Application → Domain → Infrastructure)
- **Package Manager**: `uv` (fast, modern Python package management)
- **Output Modes**: JSON (for AI agents) and Rich tables (for humans)

## Setup Commands

### Quick Setup

```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Set required environment variables
export WORKOUTER_API_URL=http://localhost:8000/graphql
export WORKOUTER_API_KEY=your-api-key-here

# Verify installation
uv run workouter-cli --help
```

### Environment Variables

**Required**:
- `WORKOUTER_API_URL`: GraphQL API endpoint (e.g., `http://localhost:8000/graphql`)
- `WORKOUTER_API_KEY`: API authentication key from the API server

**Optional**:
- `WORKOUTER_CLI_TIMEOUT`: Request timeout in seconds (default: 30)
- `WORKOUTER_CLI_LOG_LEVEL`: Log level - DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
- `WORKOUTER_CLI_LOG_FILE`: Optional log file path (empty = stderr only)

## Development Workflow

### Starting the CLI

```bash
# Run CLI in development mode
uv run workouter-cli --help

# Run specific command
uv run workouter-cli exercises list

# Run with JSON output (for AI agents)
uv run workouter-cli --json exercises list

# Run with timeout override
uv run workouter-cli --timeout 60 exercises list
```

### Development Server (API)

The CLI requires the Workouter API to be running. From the `api/` directory:

```bash
# Start API server (from api/ directory)
cd ../api
make dev
# Or manually: uv run uvicorn app.main:create_app --factory --reload
```

### Making Changes

1. **Edit code** in `src/workouter_cli/`
2. **Run linter**: `make lint` or `uv run ruff check .`
3. **Format code**: `make format` or `uv run ruff format .`
4. **Run tests**: `make test` or `uv run pytest`
5. **Check types**: `make type-check` or `uv run mypy src`

## Testing Instructions

### Quick Commands

```bash
# Run all tests
make test
# Or: uv run pytest

# Run unit tests only
make test-unit
# Or: uv run pytest tests/unit

# Run integration tests only
make test-integration
# Or: uv run pytest tests/integration

# Run with coverage
make test-cov
# Or: uv run pytest --cov=workouter_cli --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_services/test_exercise_service.py

# Run specific test
uv run pytest tests/unit/test_services/test_exercise_service.py::test_list_exercises_success

# Run with verbose output
uv run pytest -v

# Run with minimal output (CI-friendly, for agents)
uv run pytest -q --tb=short --disable-warnings
```

### Testing Strategy

- **Unit tests** (`tests/unit/`): Service layer, formatters, validators in isolation
  - All repositories mocked with `pytest-mock`
  - No real GraphQL calls
  - Coverage target: ≥ 90%

- **Integration tests** (`tests/integration/`): Full CLI commands with mocked GraphQL responses
  - Uses Click's `CliRunner`
  - All backend mocked (no real API calls)
  - Coverage target: ≥ 80%

- **Important**: ALL tests mock the GraphQL client. No real API calls are made during testing.

### Test Debugging

For failing tests:
1. Run individually: `uv run pytest path/to/test.py::test_name -vv`
2. Use `--pdb` flag to drop into debugger on failure
3. Check mock setup in `tests/conftest.py`
4. Verify mock GraphQL responses in `tests/fixtures/graphql_responses.py`

## Code Style

### Conventions

- **PEP 8** compliance (enforced by ruff)
- **Type hints**: 100% coverage using Python 3.14+ syntax (`|` for unions, `list[]`/`dict[]` for collections)
- **Async**: Use `async`/`await` for all I/O operations (GraphQL calls)
- **Imports**: Absolute imports starting with `workouter_cli.`
- **Naming**:
  - snake_case for functions, variables, modules
  - PascalCase for classes
  - SCREAMING_SNAKE_CASE for constants

### Layer Organization

```
Presentation (CLI Commands)
    ↓ depends on
Application (Services / Orchestration)
    ↓ depends on
Domain (Entities / Protocols)
    ↑ implemented by
Infrastructure (GraphQL / Config)
```

**Dependency Rule**: Inner layers (Domain) never import from outer layers (Application, Presentation, Infrastructure).

### Linting and Formatting

```bash
# Check code style
make lint
# Or: uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
make format
# Or: uv run ruff format .

# Type checking
make type-check
# Or: uv run mypy src
```

### File Organization

- **Domain**: Pure Python entities, enums, protocols (no external dependencies)
- **Application**: Services (business logic), DTOs, formatters
- **Infrastructure**: GraphQL client, repositories, config loading
- **Presentation**: Click commands, CLI entry point, output formatting

## Build and Deployment

### Local Build

```bash
# Install in development mode
uv pip install -e .

# Build package
uv build

# Output: dist/workouter_cli-0.1.0-py3-none-any.whl
```

### Docker Build

```bash
# Build Docker image (includes tests)
docker build -t workouter-cli .

# Run CLI in Docker
docker run --rm \
  -e WORKOUTER_API_URL=http://host.docker.internal:8000/graphql \
  -e WORKOUTER_API_KEY=your-key \
  workouter-cli exercises list --json
```

**Note**: The Dockerfile uses multi-stage builds with a test stage. Build will fail if tests don't pass.

## Command Structure

### High-Level Command Groups

```bash
workouter-cli
├── workout          # Workflow commands (start, log, complete, today)
├── exercises        # Exercise CRUD operations
├── routines         # Routine management
├── mesocycles       # Mesocycle management
├── sessions         # Session management
├── bodyweight       # Bodyweight logging
├── insights         # Training insights (volume, intensity, overload)
├── calendar         # Calendar view (day, range)
├── backup           # Backup trigger
└── schema           # Output example JSON for any command
```

### Common Patterns

#### List Commands
```bash
workouter-cli exercises list [--page INT] [--page-size INT] [--json]
```

#### Get Commands
```bash
workouter-cli exercises get <UUID> [--json]
```

#### Create Commands
```bash
workouter-cli exercises create --name "Exercise Name" [--description TEXT] [--json] [--dry-run]
```

#### Update Commands
```bash
workouter-cli exercises update <UUID> [--name TEXT] [--json] [--dry-run]
```

#### Delete Commands
```bash
workouter-cli exercises delete <UUID> [--json] [--force]
```

### AI-Agent Optimized Features

**Global `--json` flag**: Returns structured JSON on all commands
```bash
workouter-cli --json exercises list | jq '.data.items[0].name'
```

**Schema introspection**: Get example output for any command
```bash
workouter-cli schema "exercises list"
```

**Semantic exit codes**:
- `0`: Success
- `1`: User error (invalid input)
- `2`: API error (GraphQL error)
- `3`: Auth error (missing/invalid API key)
- `4`: Network error (timeout, connection failed)

**No interactive prompts**: All inputs via flags/args, use `--force` for confirmations

**Stateless**: No local state files, all context via env vars and flags

## Pull Request Guidelines

Before submitting a PR:

1. **Run all checks**:
   ```bash
   make lint    # Ruff linting
   make format  # Code formatting
   make type-check  # Mypy type checking
   make test    # All tests
   ```

2. **PR Title Format**: `[Component] Brief description`
   - Examples:
     - `[Commands] Add bodyweight logging commands`
     - `[Services] Implement workout workflow service`
     - `[Tests] Add integration tests for session commands`

3. **Ensure**:
   - All tests pass (≥ 85% coverage)
   - Code is formatted (ruff)
   - Types are valid (mypy)
   - No linting errors (ruff)

4. **Commit message**: Follow conventional commits style
   - `feat:` for new features
   - `fix:` for bug fixes
   - `refactor:` for code refactoring
   - `test:` for test additions/changes
   - `docs:` for documentation

## Additional Notes

### Working with GraphQL

- **Queries/Mutations**: Located in `src/workouter_cli/infrastructure/graphql/queries/` and `mutations/`
- **Schema**: Refer to `api/schema.graphql` for available operations
- **Mappers**: GraphQL response → domain entity mapping in `infrastructure/graphql/mappers/`

### Common Issues

1. **"Missing API key" error**:
   - Set `WORKOUTER_API_KEY` environment variable
   - Verify API key is valid (test with curl to API)

2. **Connection refused**:
   - Ensure API server is running on specified URL
   - Check `WORKOUTER_API_URL` matches API server address

3. **Import errors during development**:
   - Ensure you're using `uv run` prefix
   - Verify `uv sync` has been run
   - Check Python version (3.14+ required)

4. **Tests failing with "mock not found"**:
   - Check `tests/conftest.py` for fixture definitions
   - Verify `pytest-mock` is installed (`uv sync`)
   - Ensure mocking follows patterns in existing tests

### Performance Considerations

- **Pagination**: Use `--page-size` to control data volume (default: 20, max: 100)
- **Timeout**: Increase `--timeout` or `WORKOUTER_CLI_TIMEOUT` for slow networks
- **Caching**: Currently no caching (stateless design); all data fetched fresh

### Debugging

**Enable debug logging**:
```bash
export WORKOUTER_CLI_LOG_LEVEL=DEBUG
uv run workouter-cli exercises list
```

**Save logs to file**:
```bash
export WORKOUTER_CLI_LOG_FILE=/tmp/workouter-cli.log
uv run workouter-cli exercises list
cat /tmp/workouter-cli.log
```

**Inspect GraphQL requests** (debug level):
```bash
WORKOUTER_CLI_LOG_LEVEL=DEBUG uv run workouter-cli exercises list 2>&1 | grep "GraphQL"
```

## Makefile Commands

Quick reference for all Makefile targets:

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev           # Run CLI in development mode
make test          # Run all tests
make test-unit     # Run unit tests only
make test-integration  # Run integration tests only
make test-cov      # Run tests with coverage report
make lint          # Run linter (ruff check)
make format        # Format code (ruff format)
make type-check    # Run type checker (mypy)
make build         # Build Docker image
make clean         # Remove cache and build artifacts
```

## Related Documentation

- **Design Document**: See `DESIGN.md` for comprehensive system design
- **API Documentation**: See `../api/DESIGN.md` for API schema and endpoints
- **GraphQL Schema**: See `../api/schema.graphql` for query/mutation definitions
- **agents.md Format**: https://agents.md/ for AGENTS.md specification
