# AGENTS.md

## Project Overview

This folder contains end-to-end tests for Workouter that exercise the real CLI against a live API process using isolated, temporary runtime data for each test.

- Scope: cross-service validation from `workouter-cli` command execution to persisted API/database state.
- Language/stack: Python, `pytest`, `uv`, local process orchestration via fixtures in `conftest.py`.
- Test style: black-box CLI calls plus API/GraphQL assertions.

## Setup Commands

- Install dependencies: `uv sync`
- Run all e2e tests: `uv run pytest -q --tb=short --disable-warnings`
- Run a single test file: `uv run pytest -q test_core_workflows.py`
- Run one test by name: `uv run pytest -q test_core_workflows.py -k workout_session_lifecycle`

Run all commands from `e2e/` unless specified otherwise.

## Development Workflow

- Primary fixtures live in `conftest.py`:
  - `api_runtime` starts/stops API with an isolated temp config/database.
  - `run_cli` executes `uv run workouter-cli ...` with the runtime API URL/key.
- Add helpers inside test modules for repeated payload parsing and assertions.
- Keep tests deterministic:
  - Use explicit names and fixed values where possible.
  - Assert API health/readiness before workflow steps when needed.
  - Avoid timing assumptions except controlled polling helpers.

## Testing Instructions

- Test files are named `test_*.py` in this directory.
- Existing suite currently includes:
  - `test_smoke.py`: runtime isolation/smoke checks.
  - `test_core_workflows.py`: high-value workflow coverage.
- For workflow tests, verify both:
  - CLI contract (`success`, `data`/`error`, semantic exit code).
  - API-side state (GraphQL query confirms persistence).
- If a test fails because API startup fails, inspect the runtime log path emitted by fixture exceptions.

## Code Style

- Follow existing `pytest` style and type hints (`from __future__ import annotations`).
- Keep helper functions small and reusable (`_assert_cli_success`, `_graphql_request`, etc.).
- Prefer meaningful assertions over snapshot-style broad payload comparisons.
- Do not introduce network calls outside local API endpoints started by fixtures.

## Pull Request Guidelines

- Before opening a PR, run:
  - `uv run pytest -q --tb=short --disable-warnings`
- PRs that add/modify e2e tests should state:
  - workflow(s) covered,
  - failure path(s) covered,
  - evidence of stable execution (command + result).

## Additional Notes

- Runtime isolation is intentional: each test gets a fresh temp database and backup directory.
- Tests should not depend on execution order unless explicitly encoded and justified.
- Use JSON CLI mode (`--json`) for machine-assertable output contracts.
