# DESIGN.md

## Workout Tracker API — System Design Document

---

## 1. Overview

A single-user Workout Tracker API built with Python, FastAPI, Strawberry GraphQL, and SQLAlchemy. The system supports structured mesocycle-based training with routines, sessions, exercises, sets (including supersets and dropsets), bodyweight tracking, progressive overload insights, and a calendar view. Security is handled via a static API key. All timestamps are UTC. Data is stored in SQLite (configurable). GraphQL is the primary query interface with a code-first schema approach.

---

## 2. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Language | Python 3.12+ | Modern typing, performance |
| Web Framework | FastAPI 0.115+ | Async, OpenAPI, middleware |
| GraphQL | Strawberry 0.243+ | Code-first, async, FastAPI integration |
| ORM | SQLAlchemy 2.0+ (async) | Modern async session, type-safe |
| DB Driver | aiosqlite (default) | Async SQLite; swappable via config |
| Migrations | Alembic 1.13+ | Schema versioning |
| Config | PyYAML + Pydantic v2 | YAML config with strict validation |
| Logging | structlog 24+ | Structured JSON logging, level config |
| Testing | pytest 8+, pytest-asyncio, pytest-cov | Modern async test support |
| Mocking | unittest.mock + factory-boy | Unit-level isolation |
| HTTP Testing | httpx (AsyncClient) | Integration testing of FastAPI |
| Package Manager | uv | Fast, modern Python package management |
| Containerization | Docker | Reproducible builds, test-on-build |
| Backup | shutil + APScheduler | Local file copy, scheduled or manual |
| Linting/Format | ruff | All-in-one linter and formatter |

---

## 3. Data Model

### 3.1 Entity-Relationship Diagram (Conceptual)

```
Mesocycle 1──* MesocycleWeek 1──* PlannedSession
Routine 1──* RoutineExercise 1──* RoutineSet
PlannedSession *──1 Routine (nullable — ad-hoc sessions allowed)

Session 1──* SessionExercise 1──* SessionSet
Session *──1 PlannedSession (nullable)
Session *──1 Mesocycle (nullable — ad-hoc sessions allowed)

Exercise *──* MuscleGroup (via ExerciseMuscleGroup)

RoutineSet has discriminator: standard | superset | dropset
SessionSet has discriminator: standard | superset | dropset

BodyweightLog (standalone, timestamped)
```

### 3.2 Table Definitions

#### `exercise`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| name | VARCHAR(200) | NOT NULL, UNIQUE |
| description | TEXT | nullable |
| equipment | VARCHAR(100) | nullable |
| created_at | TIMESTAMP | NOT NULL, UTC |
| updated_at | TIMESTAMP | NOT NULL, UTC |

#### `muscle_group`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| name | VARCHAR(100) | NOT NULL, UNIQUE |

Seed values: Chest, Back, Shoulders, Biceps, Triceps, Forearms, Quadriceps, Hamstrings, Glutes, Calves, Abs, Traps, Lats, Neck, Hip Flexors, Adductors, Abductors.

#### `exercise_muscle_group`
| Column | Type | Constraints |
|---|---|---|
| exercise_id | UUID (FK → exercise) | PK |
| muscle_group_id | UUID (FK → muscle_group) | PK |
| role | ENUM('primary','secondary') | NOT NULL |

#### `mesocycle`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| name | VARCHAR(200) | NOT NULL |
| description | TEXT | nullable |
| start_date | DATE | NOT NULL |
| end_date | DATE | nullable (computed or explicit) |
| status | ENUM('planned','active','completed') | NOT NULL, default 'planned' |
| created_at | TIMESTAMP | NOT NULL, UTC |
| updated_at | TIMESTAMP | NOT NULL, UTC |

#### `mesocycle_week`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| mesocycle_id | UUID (FK → mesocycle) | NOT NULL |
| week_number | INTEGER | NOT NULL (1-indexed) |
| week_type | ENUM('training','deload') | NOT NULL |
| start_date | DATE | NOT NULL |
| end_date | DATE | NOT NULL |
| UNIQUE | (mesocycle_id, week_number) | |

#### `routine`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| name | VARCHAR(200) | NOT NULL |
| description | TEXT | nullable |
| created_at | TIMESTAMP | NOT NULL, UTC |
| updated_at | TIMESTAMP | NOT NULL, UTC |

#### `routine_exercise`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| routine_id | UUID (FK → routine) | NOT NULL |
| exercise_id | UUID (FK → exercise) | NOT NULL |
| order | INTEGER | NOT NULL |
| superset_group | INTEGER | nullable (exercises sharing a group # are supersetted) |
| rest_seconds | INTEGER | nullable (default rest between sets) |
| notes | TEXT | nullable |
| UNIQUE | (routine_id, order) | |

#### `routine_set`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| routine_exercise_id | UUID (FK → routine_exercise) | NOT NULL |
| set_number | INTEGER | NOT NULL (1-indexed within exercise) |
| set_type | ENUM('standard','dropset') | NOT NULL, default 'standard' |
| target_reps_min | INTEGER | nullable |
| target_reps_max | INTEGER | nullable |
| target_rir | INTEGER | nullable (reps in reserve) |
| target_weight_kg | DECIMAL(7,2) | nullable |
| weight_reduction_pct | DECIMAL(5,2) | nullable (for dropsets, e.g. 20.00 = 20%) |
| rest_seconds | INTEGER | nullable |
| UNIQUE | (routine_exercise_id, set_number) | |

*Note: Supersets are modeled at the `routine_exercise` level via `superset_group`. Dropsets are modeled at the `routine_set` level via `set_type` + `weight_reduction_pct`.*

#### `planned_session`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| mesocycle_week_id | UUID (FK → mesocycle_week) | NOT NULL |
| routine_id | UUID (FK → routine) | nullable (null = rest day or TBD) |
| day_of_week | INTEGER | NOT NULL (0=Mon, 6=Sun) |
| date | DATE | NOT NULL |
| notes | TEXT | nullable |
| UNIQUE | (mesocycle_week_id, date) | |

#### `session`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| planned_session_id | UUID (FK → planned_session) | nullable (null = ad-hoc) |
| mesocycle_id | UUID (FK → mesocycle) | nullable |
| routine_id | UUID (FK → routine) | nullable (template used; null if fully ad-hoc) |
| status | ENUM('planned','in_progress','completed') | NOT NULL, default 'planned' |
| started_at | TIMESTAMP | nullable, UTC |
| completed_at | TIMESTAMP | nullable, UTC |
| notes | TEXT | nullable |
| created_at | TIMESTAMP | NOT NULL, UTC |
| updated_at | TIMESTAMP | NOT NULL, UTC |

#### `session_exercise`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| session_id | UUID (FK → session) | NOT NULL |
| exercise_id | UUID (FK → exercise) | NOT NULL |
| order | INTEGER | NOT NULL |
| superset_group | INTEGER | nullable |
| rest_seconds | INTEGER | nullable |
| notes | TEXT | nullable |
| UNIQUE | (session_id, order) | |

#### `session_set`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| session_exercise_id | UUID (FK → session_exercise) | NOT NULL |
| set_number | INTEGER | NOT NULL |
| set_type | ENUM('standard','dropset') | NOT NULL |
| target_reps | INTEGER | nullable |
| target_rir | INTEGER | nullable |
| target_weight_kg | DECIMAL(7,2) | nullable |
| actual_reps | INTEGER | nullable |
| actual_rir | INTEGER | nullable |
| actual_weight_kg | DECIMAL(7,2) | nullable |
| weight_reduction_pct | DECIMAL(5,2) | nullable |
| rest_seconds | INTEGER | nullable |
| performed_at | TIMESTAMP | nullable, UTC |
| UNIQUE | (session_exercise_id, set_number) | |

#### `bodyweight_log`
| Column | Type | Constraints |
|---|---|---|
| id | UUID (PK) | |
| weight_kg | DECIMAL(5,2) | NOT NULL |
| recorded_at | TIMESTAMP | NOT NULL, UTC |
| notes | TEXT | nullable |
| created_at | TIMESTAMP | NOT NULL, UTC |

### 3.3 Deletion Referential Integrity Rules

| Deleting | Blocked If Referenced By | Cascade Deletes |
|---|---|---|
| Exercise | routine_exercise, session_exercise, exercise_muscle_group | exercise_muscle_group |
| MuscleGroup | exercise_muscle_group | — (block) |
| Routine | planned_session (if any linked), session (if any linked) | routine_exercise → routine_set |
| RoutineExercise | — | routine_set |
| Mesocycle | session (if any linked) | mesocycle_week → planned_session |
| MesocycleWeek | session via planned_session | planned_session |
| Session | — | session_exercise → session_set |
| PlannedSession | session (if any linked) | — (block) |

All deletions that would orphan or corrupt data return a `400` / GraphQL error with explanation.

---

## 4. Architecture

### 4.1 Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│  Presentation (API / GraphQL)           │  ← Strawberry types, resolvers, FastAPI routes
├─────────────────────────────────────────┤
│  Application (Use Cases / Services)     │  ← Business logic, orchestration, DTOs
├─────────────────────────────────────────┤
│  Domain (Entities / Value Objects)      │  ← Pure Python classes, enums, interfaces
├─────────────────────────────────────────┤
│  Infrastructure (DB / External)         │  ← SQLAlchemy models, repositories, backup
└─────────────────────────────────────────┘
```

**Dependency Rule**: Inner layers never import from outer layers. Dependencies point inward. Interfaces (protocols/ABCs) are defined in Domain; implementations live in Infrastructure.

### 4.2 Key Design Patterns

| Pattern | Usage |
|---|---|
| Repository | Abstract data access; one repo per aggregate root |
| Unit of Work | Transaction management wrapping repository operations |
| Service Layer | Orchestrates use cases, enforces business rules |
| Dependency Injection | FastAPI `Depends()` + custom providers; constructor injection |
| DTO / Input/Output | Strawberry `@strawberry.input` / `@strawberry.type` separate from domain |
| Strategy | Set type handling (standard, dropset) via polymorphic resolution |
| Factory | Session creation from routine template |

### 4.3 Folder Structure

```
workout-tracker/
├── DESIGN.md
├── AGENTS.md
├── README.md
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── config.example.yaml
├── config.yaml                    # git-ignored
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial.py
│
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py                # FastAPI app factory
│       │
│       ├── config/
│       │   ├── __init__.py
│       │   ├── schema.py          # Pydantic v2 models for config validation
│       │   └── loader.py          # YAML loading + validation at startup
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
│       │   │   └── common.py      # Base entity, value objects
│       │   ├── enums.py           # SetType, SessionStatus, WeekType, MuscleRole, MesocycleStatus
│       │   ├── exceptions.py      # Domain-specific exceptions
│       │   └── repositories/
│       │       ├── __init__.py
│       │       ├── base.py        # Abstract repository protocol
│       │       ├── exercise.py
│       │       ├── muscle_group.py
│       │       ├── routine.py
│       │       ├── mesocycle.py
│       │       ├── session.py
│       │       └── bodyweight.py
│       │
│       ├── application/
│       │   ├── __init__.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── exercise_service.py
│       │   │   ├── muscle_group_service.py
│       │   │   ├── routine_service.py
│       │   │   ├── mesocycle_service.py
│       │   │   ├── session_service.py
│       │   │   ├── bodyweight_service.py
│       │   │   ├── insight_service.py     # Volume, intensity, progressive overload
│       │   │   ├── calendar_service.py    # Day-based routine lookup, completion status
│       │   │   └── backup_service.py
│       │   ├── dto/
│       │   │   ├── __init__.py
│       │   │   ├── pagination.py          # PaginationInput, PaginatedResult
│       │   │   ├── exercise.py
│       │   │   ├── routine.py
│       │   │   ├── mesocycle.py
│       │   │   ├── session.py
│       │   │   ├── bodyweight.py
│       │   │   └── insight.py
│       │   └── interfaces/
│       │       ├── __init__.py
│       │       └── unit_of_work.py        # UoW abstract
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── database/
│       │   │   ├── __init__.py
│       │   │   ├── connection.py          # Engine, async session factory
│       │   │   ├── models/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── base.py            # DeclarativeBase, mixins (UUID PK, timestamps)
│       │   │   │   ├── exercise.py
│       │   │   │   ├── muscle_group.py
│       │   │   │   ├── routine.py
│       │   │   │   ├── mesocycle.py
│       │   │   │   ├── session.py
│       │   │   │   └── bodyweight.py
│       │   │   └── repositories/
│       │   │       ├── __init__.py
│       │   │       ├── base.py            # SQLAlchemy base repository impl
│       │   │       ├── exercise.py
│       │   │       ├── muscle_group.py
│       │   │       ├── routine.py
│       │   │       ├── mesocycle.py
│       │   │       ├── session.py
│       │   │       └── bodyweight.py
│       │   ├── unit_of_work.py            # SQLAlchemy UoW implementation
│       │   ├── backup/
│       │   │   ├── __init__.py
│       │   │   ├── manager.py             # Backup logic: copy, rotate, schedule
│       │   │   └── scheduler.py           # APScheduler integration
│       │   └── seed.py                    # Muscle group seed data
│       │
│       ├── presentation/
│       │   ├── __init__.py
│       │   ├── graphql/
│       │   │   ├── __init__.py
│       │   │   ├── schema.py              # Strawberry schema root (Query, Mutation)
│       │   │   ├── context.py             # GraphQL context (services, auth)
│       │   │   ├── types/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── exercise.py
│       │   │   │   ├── muscle_group.py
│       │   │   │   ├── routine.py
│       │   │   │   ├── mesocycle.py
│       │   │   │   ├── session.py
│       │   │   │   ├── bodyweight.py
│       │   │   │   ├── insight.py
│       │   │   │   ├── calendar.py
│       │   │   │   └── pagination.py
│       │   │   ├── inputs/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── exercise.py
│       │   │   │   ├── routine.py
│       │   │   │   ├── mesocycle.py
│       │   │   │   ├── session.py
│       │   │   │   ├── bodyweight.py
│       │   │   │   └── pagination.py
│       │   │   ├── resolvers/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── exercise.py
│       │   │   │   ├── muscle_group.py
│       │   │   │   ├── routine.py
│       │   │   │   ├── mesocycle.py
│       │   │   │   ├── session.py
│       │   │   │   ├── bodyweight.py
│       │   │   │   ├── insight.py
│       │   │   │   ├── calendar.py
│       │   │   │   └── backup.py
│       │   │   └── mutations/
│       │   │       ├── __init__.py
│       │   │       ├── exercise.py
│       │   │       ├── routine.py
│       │   │       ├── mesocycle.py
│       │   │       ├── session.py
│       │   │       ├── bodyweight.py
│       │   │       └── backup.py
│       │   ├── rest/
│       │   │   ├── __init__.py
│       │   │   └── health.py              # GET /health, GET /docs (OpenAPI)
│       │   └── middleware/
│       │       ├── __init__.py
│       │       ├── auth.py                # API key middleware
│       │       ├── logging.py             # Request/response logging
│       │       └── error_handler.py       # Global exception → GraphQL error mapping
│       │
│       └── dependencies.py                # FastAPI dependency providers (DI wiring)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                        # Shared fixtures: async engine, test DB, client
│   ├── factories/
│   │   ├── __init__.py
│   │   ├── exercise.py
│   │   ├── routine.py
│   │   ├── mesocycle.py
│   │   ├── session.py
│   │   └── bodyweight.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_exercise_service.py
│   │   ├── test_routine_service.py
│   │   ├── test_mesocycle_service.py
│   │   ├── test_session_service.py
│   │   ├── test_bodyweight_service.py
│   │   ├── test_insight_service.py
│   │   ├── test_calendar_service.py
│   │   ├── test_backup_service.py
│   │   └── test_config_validation.py
│   └── integration/
│       ├── __init__.py
│       ├── test_exercise_api.py
│       ├── test_routine_api.py
│       ├── test_mesocycle_api.py
│       ├── test_session_api.py
│       ├── test_bodyweight_api.py
│       ├── test_insight_api.py
│       ├── test_calendar_api.py
│       ├── test_backup_api.py
│       └── test_auth.py
│
├── backups/                               # git-ignored, local backup storage
│   └── .gitkeep
│
└── scripts/
    ├── seed_muscle_groups.py
    └── run_migrations.py
```

---

## 5. Configuration

### 5.1 `config.example.yaml`

```yaml
# Workout Tracker API Configuration
# Copy to config.yaml and customize.

server:
  host: "0.0.0.0"                    # Bind address
  port: 8000                          # Bind port
  debug: false                        # Enable debug mode (never in production)

database:
  url: "sqlite+aiosqlite:///./data/workout_tracker.db"  # Any SQLAlchemy async URL
  echo: false                         # Log SQL statements

auth:
  api_key: "CHANGE-ME-TO-A-SECURE-KEY"  # Static API key for all requests

logging:
  level: "INFO"                       # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "json"                      # "json" or "console"
  file: null                          # Optional log file path; null = stdout only

backup:
  enabled: true                       # Enable backup system
  directory: "./backups"              # Local directory for backups
  scheduled:
    enabled: false                    # Enable scheduled backups
    frequency_hours: 24               # Interval in hours
  max_backups: 10                     # Max number of backup files retained (FIFO rotation)

pagination:
  default_page_size: 20               # Default items per page
  max_page_size: 100                  # Maximum allowed items per page
```

### 5.2 Validation (Pydantic v2)

At startup, `config/loader.py` reads `config.yaml` (path overridable via `CONFIG_PATH` env var), parses it with PyYAML, and validates via a Pydantic `BaseModel` tree. The application fails fast with a clear error if any field is missing, wrongly typed, or out of range.

---

## 6. API Design (GraphQL)

### 6.1 Schema Overview

All operations go through a single GraphQL endpoint: `POST /graphql`

Additionally:
- `GET /health` — health check (REST)
- `GET /docs` — OpenAPI spec (auto-generated by FastAPI, documents health + GraphQL endpoint)
- GraphQL Playground available at `/graphql` in debug mode

### 6.2 Query Catalog

#### Exercises & Muscle Groups
```graphql
exercises(pagination: PaginationInput, muscleGroupId: UUID): PaginatedExercises
exercise(id: UUID!): Exercise
muscleGroups: [MuscleGroup!]!
```

#### Routines
```graphql
routines(pagination: PaginationInput): PaginatedRoutines
routine(id: UUID!): Routine                    # Includes exercises, sets, superset groups
```

#### Mesocycles
```graphql
mesocycles(pagination: PaginationInput, status: MesocycleStatus): PaginatedMesocycles
mesocycle(id: UUID!): Mesocycle                 # Includes weeks, planned sessions
```

#### Sessions
```graphql
sessions(pagination: PaginationInput, status: SessionStatus, mesocycleId: UUID, dateFrom: Date, dateTo: Date): PaginatedSessions
session(id: UUID!): Session                     # Includes exercises, sets with actuals
```

#### Calendar
```graphql
calendarDay(date: Date!): CalendarDay           # Routine for that day, completion status
calendarRange(startDate: Date!, endDate: Date!): [CalendarDay!]!
```

#### Insights
```graphql
mesocycleVolumeInsight(mesocycleId: UUID!, muscleGroupId: UUID): VolumeInsight
mesocycleIntensityInsight(mesocycleId: UUID!): IntensityInsight
progressiveOverloadInsight(mesocycleId: UUID!, exerciseId: UUID!): ProgressiveOverloadInsight
exerciseHistory(exerciseId: UUID!, pagination: PaginationInput): PaginatedExerciseHistory
```

#### Bodyweight
```graphql
bodyweightLogs(pagination: PaginationInput, dateFrom: Date, dateTo: Date): PaginatedBodyweightLogs
```

### 6.3 Mutation Catalog

#### Exercises
```graphql
createExercise(input: CreateExerciseInput!): Exercise!
updateExercise(id: UUID!, input: UpdateExerciseInput!): Exercise!
deleteExercise(id: UUID!): Boolean!
assignMuscleGroups(exerciseId: UUID!, muscleGroupIds: [MuscleGroupAssignmentInput!]!): Exercise!
```

#### Routines
```graphql
createRoutine(input: CreateRoutineInput!): Routine!
updateRoutine(id: UUID!, input: UpdateRoutineInput!): Routine!
deleteRoutine(id: UUID!): Boolean!
addRoutineExercise(routineId: UUID!, input: AddRoutineExerciseInput!): Routine!
updateRoutineExercise(id: UUID!, input: UpdateRoutineExerciseInput!): RoutineExercise!
removeRoutineExercise(id: UUID!): Boolean!
addRoutineSet(routineExerciseId: UUID!, input: AddRoutineSetInput!): RoutineExercise!
updateRoutineSet(id: UUID!, input: UpdateRoutineSetInput!): RoutineSet!
removeRoutineSet(id: UUID!): Boolean!
```

#### Mesocycles
```graphql
createMesocycle(input: CreateMesocycleInput!): Mesocycle!
updateMesocycle(id: UUID!, input: UpdateMesocycleInput!): Mesocycle!
deleteMesocycle(id: UUID!): Boolean!
addMesocycleWeek(mesocycleId: UUID!, input: AddMesocycleWeekInput!): MesocycleWeek!
updateMesocycleWeek(id: UUID!, input: UpdateMesocycleWeekInput!): MesocycleWeek!
removeMesocycleWeek(id: UUID!): Boolean!
addPlannedSession(mesocycleWeekId: UUID!, input: AddPlannedSessionInput!): PlannedSession!
updatePlannedSession(id: UUID!, input: UpdatePlannedSessionInput!): PlannedSession!
removePlannedSession(id: UUID!): Boolean!
```

#### Sessions
```graphql
createSession(input: CreateSessionInput!): Session!                         # Ad-hoc or from planned
startSession(id: UUID!): Session!                                           # Sets started_at, status → in_progress
completeSession(id: UUID!): Session!                                        # Sets completed_at, status → completed
updateSession(id: UUID!, input: UpdateSessionInput!): Session!              # Edit timestamps, notes, status
deleteSession(id: UUID!): Boolean!
addSessionExercise(sessionId: UUID!, input: AddSessionExerciseInput!): Session!
updateSessionExercise(id: UUID!, input: UpdateSessionExerciseInput!): SessionExercise!
removeSessionExercise(id: UUID!): Boolean!
addSessionSet(sessionExerciseId: UUID!, input: AddSessionSetInput!): SessionExercise!
updateSessionSet(id: UUID!, input: UpdateSessionSetInput!): SessionSet!
removeSessionSet(id: UUID!): Boolean!
logSetResult(setId: UUID!, input: LogSetResultInput!): SessionSet!          # Record actual reps, rir, weight
```

#### Bodyweight
```graphql
logBodyweight(input: LogBodyweightInput!): BodyweightLog!
updateBodyweightLog(id: UUID!, input: UpdateBodyweightInput!): BodyweightLog!
deleteBodyweightLog(id: UUID!): Boolean!
```

#### Backup
```graphql
triggerBackup: BackupResult!
```

### 6.4 Key Input / Type Shapes

```graphql
input CreateSessionInput {
  plannedSessionId: UUID          # null → ad-hoc session
  mesocycleId: UUID               # optional context
  routineId: UUID                 # if provided, pre-populates from routine template
  notes: String
}

input LogSetResultInput {
  actualReps: Int!
  actualRir: Int!
  actualWeightKg: Float!
  performedAt: DateTime           # defaults to now() UTC
}

type CalendarDay {
  date: Date!
  plannedSession: PlannedSession
  session: Session                # null if not yet created
  isCompleted: Boolean!
  isRestDay: Boolean!
}

type VolumeInsight {
  mesocycleId: UUID!
  weeklyVolumes: [WeeklyVolume!]!     # sets per muscle group per week
  totalSets: Int!
  muscleGroupBreakdown: [MuscleGroupVolume!]!
}

type ProgressiveOverloadInsight {
  exerciseId: UUID!
  mesocycleId: UUID!
  weeklyProgress: [WeeklyExerciseProgress!]!  # max weight, avg reps, avg rir per week
  estimatedOneRepMaxProgression: [Float!]!
}
```

### 6.5 Pagination

All list queries accept:
```graphql
input PaginationInput {
  page: Int = 1        # 1-indexed
  pageSize: Int = 20   # capped by config.pagination.max_page_size
}

type PaginatedExercises {
  items: [Exercise!]!
  total: Int!
  page: Int!
  pageSize: Int!
  totalPages: Int!
}
```

---

## 7. Authentication & Security

- All requests (except `GET /health`) require the header:
  ```
  Authorization: Bearer <api_key>
  ```
- Middleware (`presentation/middleware/auth.py`) validates the key against `config.auth.api_key`.
- On mismatch: `401 Unauthorized` (REST) or GraphQL error with `UNAUTHORIZED` extension code.
- The GraphQL playground is only available when `server.debug` is `true`.

---

## 8. Logging

- **structlog** configured at startup based on `config.logging`.
- Processors: timestamp (UTC ISO8601), log level, caller info, JSON or console renderer.
- Request middleware logs: method, path, status, duration_ms, request_id (UUID per request).
- Service layer logs: operation, entity_id, outcome.
- Log level dynamically applied from config: `DEBUG` includes SQL echo; `INFO` is standard; `WARNING+` for production.

---

## 9. Backup System

### 9.1 Manual Trigger
- GraphQL mutation `triggerBackup` copies the SQLite file (or dumps if non-SQLite) to `config.backup.directory` with timestamp filename: `backup_20241215_143022.db`.
- Returns `BackupResult { success, filename, sizeBytes, createdAt }`.

### 9.2 Scheduled
- If `config.backup.scheduled.enabled == true`, an APScheduler `AsyncIOScheduler` runs a backup job every `frequency_hours`.
- On each backup, the system checks file count vs `max_backups` and deletes the oldest if exceeded.

### 9.3 Implementation
- For SQLite: file copy using `shutil.copy2` after acquiring a checkpoint (`PRAGMA wal_checkpoint(FULL)`).
- For other databases: the backup endpoint returns an error indicating that only SQLite backup is supported (extensible in the future).

---

## 10. Dockerfile

```dockerfile
FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy source
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

# Install the project itself
RUN uv sync --frozen --no-dev

# --- Test stage ---
FROM base AS test

RUN uv sync --frozen

COPY tests/ tests/
COPY config.example.yaml config.yaml

# Run all tests — build fails if tests fail
RUN uv run pytest tests/ -v --tb=short --strict-markers

# --- Production stage ---
FROM base AS production

COPY config.example.yaml config.example.yaml

RUN mkdir -p /app/data /app/backups

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 11. Testing Strategy

### 11.1 Unit Tests
- **Scope**: Service layer methods in isolation.
- **Mocking**: Repository interfaces mocked with `unittest.mock.AsyncMock`. UoW mocked.
- **Framework**: `pytest` + `pytest-asyncio`.
- **Coverage target**: ≥ 85% on `application/services/`.
- **Examples**:
  - `test_exercise_service.py`: create, update, delete (with referential check), list with pagination.
  - `test_insight_service.py`: volume calculation, progressive overload math.
  - `test_config_validation.py`: valid + invalid YAML scenarios.

### 11.2 Integration Tests
- **Scope**: Full request → DB → response cycle.
- **Setup**: In-memory SQLite (`sqlite+aiosqlite://`), tables created via `create_all` per test module (or session-scoped fixture). Alembic not used in tests—schema from models directly.
- **Client**: `httpx.AsyncClient` with `ASGITransport` against the FastAPI app.
- **Auth**: Tests include the API key header; one test suite validates rejection without it.
- **Data**: `factory-boy` factories produce valid entities for setup.
- **Examples**:
  - Full CRUD cycle for each entity via GraphQL mutations/queries.
  - Deletion blocked when references exist.
  - Session lifecycle: create → start → log sets → complete.
  - Calendar query returns correct data.
  - Backup mutation creates file on disk (using `tmp_path`).

### 11.3 Factories (`tests/factories/`)
- Use `factory.Factory` (or `factory.alchemy.SQLAlchemyModelFactory` for integration) to produce valid instances with sensible defaults and sequences.

---

## 12. OpenAPI Documentation

FastAPI auto-generates an OpenAPI 3.1 spec. Enhanced with:
- `title`, `version`, `description` set in `create_app`.
- REST endpoint (`/health`) fully documented with response models.
- GraphQL endpoint documented as `POST /graphql` with `application/json` body.
- Security scheme documented (`HTTPBearer`).
- Available at `GET /docs` (Swagger UI) and `GET /openapi.json`.

---

## 13. Key Business Rules

1. **Session creation from routine**: When `CreateSessionInput.routineId` is provided, the service copies all `routine_exercise` → `session_exercise` and `routine_set` → `session_set` (with targets copied, actuals null). The user can then modify the session freely.
2. **Ad-hoc sessions**: Sessions with no `routineId` and no `plannedSessionId` are fully ad-hoc. Exercises and sets are added manually.
3. **Status transitions**: `planned` → `in_progress` → `completed`. No backward transitions. `startSession` sets `started_at = now()`. `completeSession` sets `completed_at = now()`.
4. **Deload weeks**: `mesocycle_week.week_type = 'deload'` is informational; insights can filter or highlight deload data differently.
5. **Progressive overload insight**: Compares estimated 1RM (Epley formula: `weight × (1 + reps/30)`) across weeks for an exercise within a mesocycle.
6. **Volume insight**: Counts total working sets per muscle group per week, considering `exercise_muscle_group` mappings.
7. **All timestamps UTC**: No timezone conversion; the API documents that all `DateTime` fields are UTC.

---

## 14. Dependency Injection Wiring

```python
# src/app/dependencies.py (simplified)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

async def get_unit_of_work(session: AsyncSession = Depends(get_db_session)) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)

async def get_exercise_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> ExerciseService:
    return ExerciseService(uow)

# ... same pattern for all services
# Strawberry resolvers access services via Info.context
```

---

## 15. Migrations (Alembic)

- `alembic.ini` configured with `sqlalchemy.url` placeholder, overridden at runtime by `env.py` reading from the app config.
- Initial migration `001_initial.py` creates all tables.
- Subsequent migrations are created via `uv run alembic revision --autogenerate -m "description"`.
- Migrations run on app startup (optional, configurable) or via `scripts/run_migrations.py`.

---

## 16. Error Handling

| Error Type | HTTP / GraphQL Handling |
|---|---|
| Validation error (input) | GraphQL error with `VALIDATION_ERROR` extension |
| Entity not found | GraphQL error with `NOT_FOUND` extension |
| Referential integrity violation | GraphQL error with `CONFLICT` extension, detail message |
| Authentication failure | 401 HTTP status (middleware) |
| Unexpected error | 500 HTTP / `INTERNAL_ERROR` extension, logged with full traceback |

All errors follow a consistent structure with `message`, `extensions.code`, and optional `extensions.details`.