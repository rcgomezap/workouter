# AGENTS.md

## Project Overview

Workouter is a full-stack workout tracking system consisting of a GraphQL API and a companion CLI. It is designed to track mesocycles, routines, sessions, and exercises with a focus on progressive overload and training insights.

- **Monorepo Structure**:
  - `api/`: FastAPI/GraphQL backend.
  - `cli/`: Click-based command-line interface.
  - `e2e/`: End-to-end tests covering both components.

## Versioning Policy

- **Synchronized Versions**: The versions of the `api` and `cli` packages must **ALWAYS** match.
- When bumping the version, update it in:
  - `api/pyproject.toml`
  - `api/src/app/version.py`
  - `cli/pyproject.toml`
  - `cli/src/workouter_cli/version.py`

## Setup and Development

### API
See `api/AGENTS.md` for detailed backend instructions.
- Install: `cd api && make install`
- Dev: `cd api && make dev`
- Test: `cd api && make test`

### CLI
See `cli/AGENTS.md` for detailed CLI instructions.
- Install: `cd cli && make install`
- Test: `cd cli && make test`

## Testing Instructions

### E2E Tests
Run end-to-end tests from the root directory:
```bash
# Ensure API is running in another terminal
uv run pytest e2e
```

## Pull Request Guidelines

- **Title Format**: `[Release] Version X.Y.Z` or `[Component] Description`
- **Synchronization**: Ensure both `api` and `cli` versions are updated if a version bump is required.
