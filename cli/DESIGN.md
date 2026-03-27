# DESIGN.md

## Workouter CLI — System Design Document

---

## 1. Overview

A Python command-line interface (CLI) for the Workouter API, optimized for both human users and AI agents. The CLI provides a hybrid command structure combining workflow-based shortcuts for common tasks and full GraphQL entity access for advanced operations. Built with clean architecture principles, the CLI emphasizes machine-readable output, stateless operation, and consistent error handling to enable seamless AI agent integration.

---

## 2. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Language | Python 3.14+ | Modern typing, performance, alignment with API |
| CLI Framework | Click 8.1+ | Industry standard, nested commands, decorators |
| GraphQL Client | gql 3.5+ | Async support, schema validation, type-safe |
| HTTP Client | httpx 0.27+ | Async HTTP, built into gql[httpx] |
| Table Rendering | rich 13+ | Beautiful CLI tables, colors, formatting |
| Config | Environment variables | Stateless, agent-friendly, 12-factor compliant |
| Logging | structlog 24+ | Structured logging, JSON format, stderr output |
| Testing | pytest 8+, pytest-asyncio, pytest-mock | Async test support, comprehensive mocking |
| Package Manager | uv | Fast, modern Python package management |
| Containerization | Docker (optional) | Reproducible builds, isolated environment |
| Linting/Format | ruff | All-in-one linter and formatter |

---

## 3. Architecture

### 3.1 Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│  Presentation (CLI Commands)            │  ← Click commands, formatters, output
├─────────────────────────────────────────┤
│  Application (Services / Orchestration) │  ← Business logic, DTOs, command handlers
├─────────────────────────────────────────┤
│  Domain (Entities / Value Objects)      │  ← Pure Python classes, enums, protocols
├─────────────────────────────────────────┤
│  Infrastructure (GraphQL / Config)      │  ← GraphQL client, repositories, env config
└─────────────────────────────────────────┘
```

**Dependency Rule**: Inner layers never import from outer layers. Dependencies point inward. Interfaces (protocols/ABCs) are defined in Domain; implementations live in Infrastructure.

### 3.2 Key Design Patterns

| Pattern | Usage |
|---|---|
| Repository | Abstract GraphQL operations; one repo per aggregate root |
| Service Layer | Orchestrates use cases, enforces business rules |
| Dependency Injection | Click context for service injection |
| DTO / Input/Output | Pydantic models separate from domain entities |
| Strategy | Output formatting (JSON vs Table) via protocol |
| Factory | Test fixture generation |
| Adapter | GraphQL response → domain entity mapping |

### 3.3 Folder Structure

```
cli/
├── DESIGN.md
├── AGENTS.md
├── README.md
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── Makefile
├── .python-version              # 3.14
│
├── src/
│   └── workouter_cli/
│       ├── __init__.py
│       ├── version.py           # __version__ = "0.1.0"
│       ├── main.py              # Click app entry point
│       │
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── entities/
│       │   │   ├── __init__.py
│       │   │   ├── exercise.py
│       │   │   ├── muscle_group.py
│       │   │   ├── routine.py
│       │   │   ├── mesocycle.py
│       │   │   ├── session.py
│       │   │   ├── bodyweight.py
│       │   │   └── common.py    # Base entity, value objects
│       │   ├── enums.py         # SetType, SessionStatus, etc.
│       │   ├── exceptions.py    # Domain-specific exceptions
│       │   └── repositories/
│       │       ├── __init__.py
│       │       ├── base.py      # Abstract repository protocol
│       │       ├── exercise.py
│       │       ├── routine.py
│       │       ├── mesocycle.py
│       │       ├── session.py
│       │       ├── bodyweight.py
│       │       ├── insight.py
│       │       ├── calendar.py
│       │       └── backup.py
│       │
│       ├── application/
│       │   ├── __init__.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── exercise_service.py
│       │   │   ├── routine_service.py
│       │   │   ├── mesocycle_service.py
│       │   │   ├── session_service.py
│       │   │   ├── bodyweight_service.py
│       │   │   ├── insight_service.py
│       │   │   ├── calendar_service.py
│       │   │   ├── backup_service.py
│       │   │   └── workflow_service.py  # High-level workflows (start, log, complete)
│       │   ├── dto/
│       │   │   ├── __init__.py
│       │   │   ├── pagination.py
│       │   │   ├── exercise.py
│       │   │   ├── routine.py
│       │   │   ├── mesocycle.py
│       │   │   ├── session.py
│       │   │   ├── bodyweight.py
│       │   │   ├── insight.py
│       │   │   └── output.py    # OutputFormat, CommandResult
│       │   └── formatters/
│       │       ├── __init__.py
│       │       ├── base.py      # Formatter protocol
│       │       ├── json.py      # JSON formatter
│       │       ├── table.py     # Rich table formatter
│       │       └── factory.py   # Formatter factory
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── config/
│       │   │   ├── __init__.py
│       │   │   ├── schema.py    # Pydantic config model
│       │   │   └── loader.py    # Load from env vars
│       │   ├── graphql/
│       │   │   ├── __init__.py
│       │   │   ├── client.py    # GraphQL client setup
│       │   │   ├── queries/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── exercise.py
│       │   │   │   ├── routine.py
│       │   │   │   ├── mesocycle.py
│       │   │   │   ├── session.py
│       │   │   │   ├── bodyweight.py
│       │   │   │   ├── insight.py
│       │   │   │   └── calendar.py
│       │   │   ├── mutations/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── exercise.py
│       │   │   │   ├── routine.py
│       │   │   │   ├── mesocycle.py
│       │   │   │   ├── session.py
│       │   │   │   ├── bodyweight.py
│       │   │   │   └── backup.py
│       │   │   └── mappers/
│       │   │       ├── __init__.py
│       │   │       └── response_mapper.py  # GraphQL response → domain entity
│       │   └── repositories/
│       │       ├── __init__.py
│       │       ├── base.py      # Base GraphQL repository
│       │       ├── exercise.py
│       │       ├── routine.py
│       │       ├── mesocycle.py
│       │       ├── session.py
│       │       ├── bodyweight.py
│       │       ├── insight.py
│       │       ├── calendar.py
│       │       └── backup.py
│       │
│       ├── presentation/
│       │   ├── __init__.py
│       │   ├── cli.py           # Main CLI group
│       │   ├── context.py       # Click context with DI
│       │   ├── options.py       # Common Click options/decorators
│       │   ├── utils.py         # CLI helpers (error handling, validation)
│       │   ├── commands/
│       │   │   ├── __init__.py
│       │   │   ├── workflow/    # High-level workflow commands
│       │   │   │   ├── __init__.py
│       │   │   │   ├── start.py
│       │   │   │   ├── log.py
│       │   │   │   ├── complete.py
│       │   │   │   └── today.py
│       │   │   ├── exercises.py
│       │   │   ├── routines.py
│       │   │   ├── mesocycles.py
│       │   │   ├── sessions.py
│       │   │   ├── bodyweight.py
│       │   │   ├── insights.py
│       │   │   ├── calendar.py
│       │   │   ├── backup.py
│       │   │   └── schema.py    # Schema introspection command
│       │   └── middleware/
│       │       ├── __init__.py
│       │       ├── error_handler.py  # Global exception handling
│       │       └── logging.py        # Structured logging setup
│       │
│       └── utils/
│           ├── __init__.py
│           ├── exit_codes.py    # Semantic exit codes
│           ├── validators.py    # Input validation helpers
│           └── date_utils.py    # Date parsing, formatting
│
└── tests/
    ├── __init__.py
    ├── conftest.py              # Shared fixtures: mock client, config
    ├── fixtures/
    │   ├── __init__.py
    │   ├── graphql_responses.py # Mock GraphQL responses
    │   └── factories.py         # Test data factories
    ├── unit/
    │   ├── __init__.py
    │   ├── test_services/
    │   │   ├── __init__.py
    │   │   ├── test_exercise_service.py
    │   │   ├── test_session_service.py
    │   │   └── test_workflow_service.py
    │   ├── test_formatters/
    │   │   ├── __init__.py
    │   │   ├── test_json_formatter.py
    │   │   └── test_table_formatter.py
    │   └── test_validators.py
    └── integration/
        ├── __init__.py
        ├── test_workflow_commands.py
        ├── test_exercise_commands.py
        ├── test_session_commands.py
        ├── test_error_handling.py
        └── test_json_output.py
```

---

## 4. Configuration (Environment Variables)

The CLI is fully stateless and configured via environment variables:

```bash
# Required
WORKOUTER_API_URL=http://localhost:8000/graphql    # GraphQL endpoint
WORKOUTER_API_KEY=your-secure-api-key-here         # API authentication key

# Optional
WORKOUTER_CLI_TIMEOUT=30          # Request timeout in seconds (default: 30)
WORKOUTER_CLI_LOG_LEVEL=INFO      # DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
WORKOUTER_CLI_LOG_FILE=           # Optional log file path; empty = stderr only
```

### 4.1 Configuration Validation (Pydantic)

```python
# infrastructure/config/schema.py

from pydantic import BaseModel, Field, HttpUrl

class Config(BaseModel):
    api_url: HttpUrl = Field(..., description="GraphQL API endpoint")
    api_key: str = Field(..., min_length=1, description="API authentication key")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout")
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    log_file: str | None = Field(default=None, description="Optional log file path")
```

**Startup behavior**:
- If `WORKOUTER_API_KEY` is missing → Exit with code 3 (auth error) and clear message
- If `WORKOUTER_API_URL` is missing → Exit with code 3 and clear message
- Invalid URL format → Exit with code 1 (user error)

---

## 5. Command Structure (Hybrid Approach)

### 5.1 High-Level Command Groups

```
workouter-cli
├── workout          # High-level workflow commands
│   ├── start
│   ├── log
│   ├── complete
│   └── today
├── exercises        # CRUD operations
│   ├── list
│   ├── get
│   ├── create
│   ├── update
│   ├── delete
│   └── assign-muscles
├── routines
│   ├── list
│   ├── get
│   ├── create
│   ├── update
│   ├── delete
│   ├── add-exercise
│   ├── update-exercise
│   ├── remove-exercise
│   ├── add-set
│   ├── update-set
│   └── remove-set
├── mesocycles
│   ├── list
│   ├── get
│   ├── create
│   ├── update
│   ├── delete
│   ├── add-week
│   ├── update-week
│   ├── remove-week
│   ├── add-session
│   ├── update-session
│   └── remove-session
├── sessions
│   ├── list
│   ├── get
│   ├── create
│   ├── start
│   ├── complete
│   ├── update
│   ├── delete
│   ├── add-exercise
│   ├── update-exercise
│   ├── remove-exercise
│   ├── add-set
│   ├── update-set
│   ├── remove-set
│   └── log-set
├── bodyweight
│   ├── log
│   ├── list
│   ├── update
│   └── delete
├── insights
│   ├── volume
│   ├── intensity
│   ├── overload
│   └── history
├── calendar
│   ├── day
│   └── range
├── backup
│   └── trigger
└── schema           # Output example JSON for any command
```

### 5.2 Workflow Commands (Quick Access)

#### `workouter-cli workout start [OPTIONS]`
**Purpose**: Start a new workout session from today's planned session or ad-hoc.

**Options**:
```
--routine-id UUID       Start from routine template
--mesocycle-id UUID     Link to mesocycle
--notes TEXT            Session notes
--json                  Output JSON
--dry-run               Validate without creating
```

**Behavior**:
1. Check `calendarDay(date=today)` for planned session
2. If found, create session from `plannedSession.routine`
3. If not found, prompt for routine or create ad-hoc
4. Call `createSession` mutation
5. Call `startSession` mutation
6. Output session ID and exercise list

**Example output (table)**:
```
✓ Session started successfully

Session ID: 550e8400-e29b-41d4-a716-446655440000
Status:     IN_PROGRESS
Started:    2026-03-26 15:30:00 UTC

Exercises:
┌───────────────────┬──────┬──────────┬─────────┐
│ Exercise          │ Sets │ Reps     │ Weight  │
├───────────────────┼──────┼──────────┼─────────┤
│ Bench Press       │ 4    │ 8-12     │ 80.0 kg │
│ Incline DB Press  │ 3    │ 10-12    │ 32.5 kg │
│ Cable Flyes       │ 3    │ 12-15    │ 15.0 kg │
└───────────────────┴──────┴──────────┴─────────┘
```

**Example output (JSON)**:
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "IN_PROGRESS",
    "started_at": "2026-03-26T15:30:00Z",
    "exercises": [
      {
        "id": "...",
        "name": "Bench Press",
        "sets": [
          {
            "set_number": 1,
            "target_reps": 10,
            "target_weight_kg": 80.0,
            "actual_reps": null,
            "actual_weight_kg": null
          }
        ]
      }
    ]
  }
}
```

#### `workouter-cli workout log [OPTIONS]`
**Purpose**: Log set results during an active workout.

**Options**:
```
--session-id UUID       Session ID (auto-detect if only one active)
--set-id UUID           Set ID to log
--reps INT              Actual reps performed
--rir INT               Reps in reserve
--weight FLOAT          Actual weight in kg
--json                  Output JSON
```

**Behavior**:
1. If no `--session-id`, query active sessions (status=IN_PROGRESS)
2. If multiple active → error, require explicit ID
3. Call `logSetResult` mutation
4. Output updated set info

#### `workouter-cli workout complete [OPTIONS]`
**Purpose**: Complete the current workout session.

**Options**:
```
--session-id UUID       Session ID (auto-detect if only one active)
--notes TEXT            Final session notes
--json                  Output JSON
```

**Behavior**:
1. Call `completeSession` mutation
2. Output session summary (duration, total sets, exercises)

#### `workouter-cli workout today [OPTIONS]`
**Purpose**: View today's planned workout.

**Options**:
```
--date DATE             Specific date (default: today)
--json                  Output JSON
```

**Behavior**:
1. Call `calendarDay(date)` query
2. Display planned routine, completion status
3. If already started, show session progress

---

### 5.3 Entity Commands (GraphQL Mirroring)

All entity commands follow consistent patterns:

#### List Commands
```bash
workouter-cli exercises list [OPTIONS]

Options:
  --muscle-group-id UUID    Filter by muscle group
  --page INT                Page number (default: 1)
  --page-size INT           Items per page (default: 20)
  --json                    Output JSON
```

#### Get Commands
```bash
workouter-cli exercises get <ID> [OPTIONS]

Arguments:
  ID                        Exercise UUID

Options:
  --json                    Output JSON
```

#### Create Commands
```bash
workouter-cli exercises create [OPTIONS]

Options:
  --name TEXT               Exercise name (required)
  --description TEXT        Exercise description
  --equipment TEXT          Equipment needed
  --json                    Output JSON
  --dry-run                 Validate without creating
```

#### Update Commands
```bash
workouter-cli exercises update <ID> [OPTIONS]

Arguments:
  ID                        Exercise UUID

Options:
  --name TEXT               New exercise name
  --description TEXT        New description
  --equipment TEXT          New equipment
  --json                    Output JSON
  --dry-run                 Validate without updating
```

#### Delete Commands
```bash
workouter-cli exercises delete <ID> [OPTIONS]

Arguments:
  ID                        Exercise UUID

Options:
  --json                    Output JSON
  --force                   Skip confirmation
```

---

## 6. AI Agent Optimization

### 6.1 JSON-First Output

**Global flag**: `--json` available on ALL commands.

**Structure**:
```json
{
  "success": true|false,
  "data": { /* command-specific data */ },
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Exercise name is required",
    "details": { /* additional context */ }
  },
  "metadata": {
    "timestamp": "2026-03-26T15:30:00Z",
    "command": "exercises create",
    "execution_time_ms": 142
  }
}
```

**Rules**:
- `stdout` contains ONLY the JSON object (one line, no pretty-print)
- `stderr` contains logs, progress indicators, warnings
- Exit codes match `success` field
- Schema is versioned and stable

### 6.2 Schema Introspection

```bash
workouter-cli schema "exercises list"
```

**Output** (example JSON with comments):
```json
{
  "command": "exercises list",
  "description": "List all exercises with optional filtering",
  "options": [
    {
      "name": "--muscle-group-id",
      "type": "UUID",
      "required": false,
      "description": "Filter exercises by muscle group"
    },
    {
      "name": "--page",
      "type": "int",
      "required": false,
      "default": 1,
      "description": "Page number for pagination"
    }
  ],
  "example_output": {
    "success": true,
    "data": {
      "items": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "name": "Bench Press",
          "description": "Compound chest exercise",
          "equipment": "Barbell",
          "muscle_groups": [
            {
              "muscle_group": {"id": "...", "name": "Chest"},
              "role": "PRIMARY"
            }
          ]
        }
      ],
      "total": 42,
      "page": 1,
      "page_size": 20,
      "total_pages": 3
    },
    "metadata": {
      "timestamp": "2026-03-26T15:30:00Z",
      "command": "exercises list",
      "execution_time_ms": 89
    }
  }
}
```

### 6.3 Semantic Exit Codes

| Code | Meaning | When |
|------|---------|------|
| 0 | Success | Command completed successfully |
| 1 | User Error | Invalid input, validation failure, user-fixable |
| 2 | API Error | GraphQL error, business logic rejection |
| 3 | Auth Error | Missing/invalid API key, 401/403 responses |
| 4 | Network Error | Connection timeout, DNS failure, 5xx errors |

**Usage in scripts**:
```bash
#!/bin/bash
workouter-cli --json exercises list
EXIT_CODE=$?

case $EXIT_CODE in
  0) echo "Success" ;;
  1) echo "Fix your input" ;;
  2) echo "API rejected the request" ;;
  3) echo "Check your API key" ;;
  4) echo "Network issue, retry later" ;;
esac
```

### 6.4 Silence the Noise

**In JSON mode** (`--json` flag):
- NO banners, ASCII art, colors, or "helpful tips" to stdout
- NO progress bars or spinners (unless to stderr)
- NO confirmation prompts (use `--force` flag or fail)
- NO interactive menus

**In Table mode** (default):
- Rich formatting allowed (colors, tables, progress bars)
- Confirmation prompts enabled
- Human-friendly messages

### 6.5 No Interactive Prompts

All commands are **non-interactive** by design:
- Required arguments must be provided via flags/args
- Confirmations handled via `--force` flag
- No `input()` calls in production code
- If data is missing → error with clear message

**Example** (delete without confirmation):
```bash
# Fails without --force (exit code 1)
workouter-cli exercises delete <id>

# Succeeds
workouter-cli exercises delete <id> --force
```

### 6.6 Stateless Operation

- NO session state stored locally
- NO "current workout" file or cache
- Every command is self-contained
- Use flags/env vars to pass context

**Anti-pattern**:
```bash
# BAD: Relies on stored state
workouter-cli workout start
workouter-cli workout log --reps 10  # How does it know which session?
```

**Correct pattern**:
```bash
# GOOD: Explicit session ID
SESSION_ID=$(workouter-cli --json workout start | jq -r '.data.session_id')
workouter-cli workout log --session-id $SESSION_ID --reps 10
```

### 6.7 Pagination

All list commands support:
```
--page INT              Page number (1-indexed, default: 1)
--page-size INT         Items per page (default: 20, max: 100)
```

**JSON output includes**:
```json
{
  "data": {
    "items": [...],
    "total": 156,
    "page": 1,
    "page_size": 20,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  }
}
```

### 6.8 Dry Run Capability

All mutation commands support `--dry-run`:
```bash
workouter-cli exercises create --name "Test" --dry-run
```

**Behavior**:
- Validate all inputs locally
- Build GraphQL mutation
- Output what WOULD be sent (in JSON mode)
- Exit without making API call
- Exit code 0 if valid, 1 if invalid

### 6.9 Timeout Control

```bash
workouter-cli --timeout 60 exercises list
```

Or via environment:
```bash
export WORKOUTER_CLI_TIMEOUT=60
workouter-cli exercises list
```

**Behavior**:
- Applies to HTTP request timeout
- On timeout → exit code 4 (network error)
- Clear error message with retry suggestion

---

## 7. Error Handling

### 7.1 Error Response Format (JSON)

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Exercise name must be between 1 and 200 characters",
    "details": {
      "field": "name",
      "value": "",
      "constraint": "min_length:1"
    }
  },
  "metadata": {
    "timestamp": "2026-03-26T15:30:00Z",
    "command": "exercises create"
  }
}
```

### 7.2 Error Codes

| Code | Category | Exit Code | Example |
|------|----------|-----------|---------|
| `VALIDATION_ERROR` | User input invalid | 1 | Missing required field |
| `NOT_FOUND` | Resource doesn't exist | 2 | Exercise ID not found |
| `CONFLICT` | Business rule violation | 2 | Cannot delete exercise (in use) |
| `AUTH_ERROR` | Authentication failed | 3 | Invalid API key |
| `UNAUTHORIZED` | No permission | 3 | API key lacks access |
| `NETWORK_ERROR` | Connection issue | 4 | Timeout, DNS failure |
| `INTERNAL_ERROR` | Unexpected error | 4 | Unhandled exception |

### 7.3 GraphQL Error Mapping

```python
# presentation/middleware/error_handler.py

def map_graphql_error(error: dict) -> CLIError:
    """Map GraphQL error to CLI error with appropriate exit code."""
    extensions = error.get("extensions", {})
    code = extensions.get("code", "INTERNAL_ERROR")
    
    if code == "VALIDATION_ERROR":
        return CLIError(code=code, message=error["message"], exit_code=1)
    elif code in ("NOT_FOUND", "CONFLICT"):
        return CLIError(code=code, message=error["message"], exit_code=2)
    elif code in ("AUTH_ERROR", "UNAUTHORIZED"):
        return CLIError(code=code, message=error["message"], exit_code=3)
    else:
        return CLIError(code="INTERNAL_ERROR", message=error["message"], exit_code=4)
```

### 7.4 Validation Before API Calls

**Local validation** (before network request):
- Required fields present
- Field types correct (UUID format, date format, numeric ranges)
- Enum values valid
- String length constraints

**Benefits**:
- Faster feedback (no network round-trip)
- Reduced API load
- Consistent error messages

---

## 8. Output Formatting

### 8.1 Strategy Pattern

```python
# application/formatters/base.py

from typing import Protocol, Any

class Formatter(Protocol):
    def format(self, data: Any, command: str) -> str:
        """Format command output for display."""
        ...

# application/formatters/json.py
class JsonFormatter:
    def format(self, data: Any, command: str) -> str:
        return json.dumps({
            "success": True,
            "data": data,
            "metadata": {
                "timestamp": datetime.now(UTC).isoformat(),
                "command": command
            }
        })

# application/formatters/table.py
class TableFormatter:
    def format(self, data: Any, command: str) -> str:
        # Use rich.table.Table for rendering
        ...
```

### 8.2 Table Output Examples

**List view**:
```
Exercises (Page 1 of 3, Total: 42)

┌──────────────────────────────────────┬────────────────┬──────────────┬─────────────────┐
│ ID                                   │ Name           │ Equipment    │ Primary Muscles │
├──────────────────────────────────────┼────────────────┼──────────────┼─────────────────┤
│ 550e8400-e29b-41d4-a716-446655440000 │ Bench Press    │ Barbell      │ Chest           │
│ 6ba7b810-9dad-11d1-80b4-00c04fd430c8 │ Squat          │ Barbell      │ Quadriceps      │
│ 7c9e6679-7425-40de-944b-e07fc1f90ae7 │ Deadlift       │ Barbell      │ Back            │
└──────────────────────────────────────┴────────────────┴──────────────┴─────────────────┘

Use --page 2 to view next page
```

**Detail view**:
```
Exercise: Bench Press
ID:          550e8400-e29b-41d4-a716-446655440000
Equipment:   Barbell
Description: Compound chest exercise performed lying on a bench

Muscle Groups:
  • Chest (Primary)
  • Triceps (Secondary)
  • Shoulders (Secondary)
```

---

## 9. GraphQL Client Implementation

### 9.1 Client Setup

```python
# infrastructure/graphql/client.py

from gql import Client
from gql.transport.httpx import HTTPXAsyncTransport
from typing import Any

class GraphQLClient:
    def __init__(self, url: str, api_key: str, timeout: int):
        transport = HTTPXAsyncTransport(
            url=url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
    
    async def execute(self, query: str, variables: dict[str, Any] | None = None) -> dict:
        async with self.client as session:
            return await session.execute(query, variable_values=variables)
```

### 9.2 Query Organization

Each query/mutation lives in its own file:

```python
# infrastructure/graphql/queries/exercise.py

from gql import gql

LIST_EXERCISES = gql("""
    query ListExercises($pagination: PaginationInput, $muscleGroupId: UUID) {
        exercises(pagination: $pagination, muscleGroupId: $muscleGroupId) {
            items {
                id
                name
                description
                equipment
                muscleGroups {
                    muscleGroup {
                        id
                        name
                    }
                    role
                }
            }
            total
            page
            pageSize
            totalPages
        }
    }
""")

GET_EXERCISE = gql("""
    query GetExercise($id: UUID!) {
        exercise(id: $id) {
            id
            name
            description
            equipment
            muscleGroups {
                muscleGroup {
                    id
                    name
                }
                role
            }
        }
    }
""")
```

### 9.3 Repository Implementation

```python
# infrastructure/repositories/exercise.py

from workouter_cli.domain.repositories.exercise import ExerciseRepository
from workouter_cli.domain.entities.exercise import Exercise
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.graphql.queries.exercise import LIST_EXERCISES, GET_EXERCISE

class GraphQLExerciseRepository(ExerciseRepository):
    def __init__(self, client: GraphQLClient):
        self.client = client
    
    async def list(self, page: int = 1, page_size: int = 20, muscle_group_id: str | None = None) -> list[Exercise]:
        variables = {
            "pagination": {"page": page, "pageSize": page_size},
            "muscleGroupId": muscle_group_id
        }
        result = await self.client.execute(LIST_EXERCISES, variables)
        return [self._map_to_entity(item) for item in result["exercises"]["items"]]
    
    def _map_to_entity(self, data: dict) -> Exercise:
        # Map GraphQL response to domain entity
        ...
```

---

## 10. Dependency Injection

### 10.1 Click Context

```python
# presentation/context.py

from dataclasses import dataclass
from workouter_cli.infrastructure.config.schema import Config
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.application.services.exercise_service import ExerciseService

@dataclass
class CLIContext:
    config: Config
    client: GraphQLClient
    exercise_service: ExerciseService
    # ... other services
```

### 10.2 Context Setup

```python
# presentation/cli.py

import click
from workouter_cli.presentation.context import CLIContext
from workouter_cli.infrastructure.config.loader import load_config

@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """Workouter CLI - Workout tracking from the command line."""
    config = load_config()
    client = GraphQLClient(config.api_url, config.api_key, config.timeout)
    
    # Initialize services
    exercise_service = ExerciseService(...)
    
    # Store in context
    ctx.obj = CLIContext(config=config, client=client, exercise_service=exercise_service, ...)
```

### 10.3 Command Usage

```python
# presentation/commands/exercises.py

import click
from workouter_cli.presentation.context import CLIContext

@click.command()
@click.option("--page", default=1, type=int)
@click.option("--page-size", default=20, type=int)
@click.option("--json", "output_json", is_flag=True)
@click.pass_obj
async def list(ctx: CLIContext, page: int, page_size: int, output_json: bool):
    """List all exercises."""
    exercises = await ctx.exercise_service.list(page=page, page_size=page_size)
    # Format and output...
```

---

## 11. Testing Strategy

### 11.1 Unit Tests

**Scope**: Service layer, formatters, validators in isolation.

**Mocking**: All repositories mocked with `pytest-mock`. No real GraphQL calls.

**Example**:
```python
# tests/unit/test_services/test_exercise_service.py

import pytest
from unittest.mock import AsyncMock
from workouter_cli.application.services.exercise_service import ExerciseService

@pytest.mark.asyncio
async def test_list_exercises_success(mocker):
    # Mock repository
    mock_repo = mocker.Mock()
    mock_repo.list = AsyncMock(return_value=[...])
    
    service = ExerciseService(exercise_repo=mock_repo)
    result = await service.list(page=1, page_size=20)
    
    assert len(result) == 2
    mock_repo.list.assert_called_once_with(page=1, page_size=20, muscle_group_id=None)
```

### 11.2 Integration Tests

**Scope**: Full CLI commands with mocked GraphQL responses.

**Setup**: Use Click's `CliRunner` with mocked GraphQL client.

**Example**:
```python
# tests/integration/test_exercise_commands.py

from click.testing import CliRunner
from workouter_cli.presentation.cli import cli

def test_exercises_list_json_output(mocker, mock_graphql_response):
    # Mock GraphQL client
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        return_value=mock_graphql_response("exercises_list")
    )
    
    runner = CliRunner()
    result = runner.invoke(cli, ["exercises", "list", "--json"])
    
    assert result.exit_code == 0
    output = json.loads(result.output)
    assert output["success"] is True
    assert "items" in output["data"]
```

### 11.3 Test Fixtures

```python
# tests/fixtures/graphql_responses.py

MOCK_RESPONSES = {
    "exercises_list": {
        "exercises": {
            "items": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Bench Press",
                    "description": "Compound chest exercise",
                    "equipment": "Barbell",
                    "muscleGroups": [...]
                }
            ],
            "total": 42,
            "page": 1,
            "pageSize": 20,
            "totalPages": 3
        }
    }
}

@pytest.fixture
def mock_graphql_response():
    def _get_response(key: str):
        return MOCK_RESPONSES[key]
    return _get_response
```

### 11.4 Coverage Target

- **Overall**: ≥ 85%
- **Services**: ≥ 90%
- **Formatters**: 100%
- **Commands**: ≥ 80%

---

## 12. Logging

### 12.1 Structured Logging (structlog)

```python
# presentation/middleware/logging.py

import structlog
from workouter_cli.infrastructure.config.schema import Config

def setup_logging(config: Config):
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() if config.log_level == "DEBUG" else structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

### 12.2 Log Output

**Always to stderr** (never stdout in JSON mode):
```
2026-03-26T15:30:12.345Z [INFO] Starting command command=exercises.list user=...
2026-03-26T15:30:12.456Z [DEBUG] GraphQL request query=LIST_EXERCISES variables={...}
2026-03-26T15:30:12.567Z [DEBUG] GraphQL response status=200 duration_ms=111
2026-03-26T15:30:12.568Z [INFO] Command completed command=exercises.list duration_ms=223
```

---

## 13. Docker Support

### 13.1 Dockerfile

```dockerfile
FROM python:3.14-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy source
COPY src/ src/

# Install the CLI
RUN uv sync --frozen --no-dev

# --- Test stage ---
FROM base AS test

RUN uv sync --frozen

COPY tests/ tests/

# Run all tests — build fails if tests fail
RUN uv run pytest tests/ -v --tb=short

# --- Production stage ---
FROM base AS production

# Create entrypoint
RUN ln -s /app/.venv/bin/workouter-cli /usr/local/bin/workouter-cli

ENTRYPOINT ["workouter-cli"]
CMD ["--help"]
```

### 13.2 Usage

```bash
# Build
docker build -t workouter-cli .

# Run
docker run --rm \
  -e WORKOUTER_API_URL=http://host.docker.internal:8000/graphql \
  -e WORKOUTER_API_KEY=your-key \
  workouter-cli exercises list --json
```

---

## 14. Development Workflow

### 14.1 Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
cd cli/
uv sync

# Set environment variables
export WORKOUTER_API_URL=http://localhost:8000/graphql
export WORKOUTER_API_KEY=your-api-key

# Run CLI
uv run workouter-cli --help
```

### 14.2 Common Commands (Makefile)

```makefile
.PHONY: help install dev test lint format type-check

help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run CLI in development mode"
	@echo "  test        - Run all tests"
	@echo "  lint        - Run linter"
	@echo "  format      - Format code"
	@echo "  type-check  - Run type checker"

install:
	uv sync

dev:
	uv run workouter-cli

test:
	uv run pytest tests/ -v

test-unit:
	uv run pytest tests/unit/ -v

test-integration:
	uv run pytest tests/integration/ -v

test-cov:
	uv run pytest --cov=workouter_cli --cov-report=term-missing

lint:
	uv run ruff check .

format:
	uv run ruff format .

type-check:
	uv run mypy src
```

---

## 15. Package Distribution

### 15.1 pyproject.toml

```toml
[project]
name = "workouter-cli"
version = "0.1.0"
description = "Command-line interface for Workouter API"
authors = [{name = "Your Name", email = "your.email@example.com"}]
requires-python = ">=3.14"
dependencies = [
    "click>=8.1.0",
    "gql[httpx]>=3.5.0",
    "rich>=13.0.0",
    "pydantic>=2.0.0",
    "structlog>=24.0.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.12.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
]

[project.scripts]
workouter-cli = "workouter_cli.main:cli"

[tool.ruff]
line-length = 100
target-version = "py314"

[tool.mypy]
python_version = "3.14"
strict = true
```

### 15.2 Installation

```bash
# From source
uv pip install -e .

# From PyPI (future)
uv pip install workouter-cli
```

---

## 16. Key Business Rules

1. **API Key Required**: All commands (except `--help`) require valid API key via `WORKOUTER_API_KEY`
2. **Date Format**: All dates are ISO 8601 format (`YYYY-MM-DD`)
3. **DateTime Format**: All datetimes are ISO 8601 with timezone (`YYYY-MM-DDTHH:MM:SSZ`)
4. **UUID Format**: All IDs are UUID v4 strings
5. **Pagination**: Default 20 items per page, max 100
6. **Timeout**: Default 30 seconds, configurable via env var
7. **Exit Codes**: Semantic codes (0=success, 1=user error, 2=API error, 3=auth, 4=network)

---

## 17. Future Enhancements

1. **Bash/Zsh Completion**: Auto-complete for commands and options
2. **Config Profiles**: Support multiple API endpoints (dev, staging, prod)
3. **Offline Mode**: Cache recent data for read operations
4. **Interactive Mode**: TUI for guided workflows (separate from AI mode)
5. **Export/Import**: Backup routines/mesocycles to YAML/JSON
6. **Plugins**: Extensible command system
7. **WebSocket Support**: Real-time session updates (if API adds subscriptions)

---

## 18. Comparison with API Design

| Aspect | API | CLI |
|--------|-----|-----|
| Language | Python 3.14+ | Python 3.14+ |
| Framework | FastAPI + Strawberry | Click |
| Data Access | SQLAlchemy → SQLite | gql → GraphQL → API |
| Architecture | Clean (4 layers) | Clean (4 layers, same structure) |
| Testing | pytest + httpx | pytest + pytest-mock (all mocked) |
| Config | YAML file | Environment variables |
| Output | GraphQL JSON | JSON or Rich tables |
| State | Stateful (database) | Stateless (API calls only) |
| Auth | API key middleware | API key in request headers |

---

## Appendix A: Complete Command Reference

See [AGENTS.md](./AGENTS.md) for full command examples and usage patterns.

---

## Appendix B: Exit Code Reference

| Code | Name | Description | Example Causes |
|------|------|-------------|----------------|
| 0 | Success | Command completed successfully | Exercise created, list retrieved |
| 1 | User Error | Invalid input or usage | Missing required flag, invalid UUID format |
| 2 | API Error | GraphQL business logic error | Exercise not found, constraint violation |
| 3 | Auth Error | Authentication/authorization failed | Missing API key, invalid key, expired key |
| 4 | Network Error | Network or server issue | Timeout, connection refused, 5xx errors |

---

## Appendix C: Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WORKOUTER_API_URL` | Yes | - | GraphQL API endpoint URL |
| `WORKOUTER_API_KEY` | Yes | - | API authentication key |
| `WORKOUTER_CLI_TIMEOUT` | No | 30 | Request timeout in seconds (1-300) |
| `WORKOUTER_CLI_LOG_LEVEL` | No | INFO | Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `WORKOUTER_CLI_LOG_FILE` | No | - | Optional log file path (empty = stderr only) |

---

**End of DESIGN.md**
