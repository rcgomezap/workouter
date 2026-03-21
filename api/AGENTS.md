# AGENTS.md

## Workout Tracker API — Agent Implementation Plan

---

## Overview

This document defines the AI coding agents, their responsibilities, execution order, dependencies, and detailed task specifications for building the Workout Tracker API. Each agent is a self-contained unit of work that produces tested, reviewed code.

**Execution Model**: Sequential with defined checkpoints. Later agents depend on artifacts from earlier ones. Each agent should validate that its prerequisites exist before starting.

---

## Agent Dependency Graph

```
Agent 0: Project Scaffold
    │
    ├──► Agent 1: Configuration System
    │       │
    │       ├──► Agent 2: Domain Layer
    │       │       │
    │       │       ├──► Agent 3: Infrastructure – Database Models & Connection
    │       │       │       │
    │       │       │       ├──► Agent 4: Infrastructure – Repositories & UoW
    │       │       │       │       │
    │       │       │       │       ├──► Agent 5: Application – Services (Core CRUD)
    │       │       │       │       │       │
    │       │       │       │       │       ├──► Agent 6: Application – Services (Insights, Calendar)
    │       │       │       │       │       │       │
    │       │       │       │       │       │       ├──► Agent 7: Presentation – GraphQL Types & Inputs
    │       │       │       │       │       │       │       │
    │       │       │       │       │       │       │       ├──► Agent 8: Presentation – Resolvers & Mutations
    │       │       │       │       │       │       │       │       │
    │       │       │       │       │       │       │       │       ├──► Agent 9: Presentation – Middleware & Auth
    │       │       │       │       │       │       │       │       │       │
    │       │       │       │       │       │       │       │       │       ├──► Agent 10: App Assembly & DI Wiring
    │       │       │       │       │       │       │       │       │       │       │
    │       │       │       │       │       │       │       │       │       │       ├──► Agent 11: Backup System
    │       │       │       │       │       │       │       │       │       │       │       │
    │       │       │       │       │       │       │       │       │       │       │       ├──► Agent 12: Unit Tests
    │       │       │       │       │       │       │       │       │       │       │       │       │
    │       │       │       │       │       │       │       │       │       │       │       │       ├──► Agent 13: Integration Tests
    │       │       │       │       │       │       │       │       │       │       │       │       │       │
    │       │       │       │       │       │       │       │       │       │       │       │       │       ├──► Agent 14: Docker & Final Polish
```

---

## Agent 0: Project Scaffold

**Goal**: Initialize the project structure, package management, and all empty directories/files.

**Prerequisites**: None.

**Tasks**:
1. Run `uv init workout-tracker` and configure `pyproject.toml` with all dependencies:
   - `fastapi[standard]>=0.115`, `uvicorn[standard]`, `strawberry-graphql[fastapi]`, `sqlalchemy[asyncio]>=2.0`, `aiosqlite`, `alembic`, `pyyaml`, `pydantic>=2.0`, `structlog`, `apscheduler>=3.10`, `httpx`
   - Dev dependencies: `pytest`, `pytest-asyncio`, `pytest-cov`, `factory-boy`, `ruff`, `mypy`
2. Create the complete folder structure as defined in DESIGN.md Section 4.3.
3. Create all `__init__.py` files (empty initially).
4. Create `config.example.yaml` with the content from DESIGN.md Section 5.1.
5. Create `.gitignore` (Python defaults + `config.yaml`, `*.db`, `backups/`, `data/`, `.venv/`).
6. Create `alembic.ini` with placeholder config.
7. Create `alembic/env.py` skeleton (async-ready, reads DB URL from app config).
8. Create `alembic/script.py.mako` standard template.
9. Run `uv sync` to verify dependency resolution.

**Outputs**: Complete project skeleton, all dependencies installable, `uv run python -c "import fastapi; import strawberry; import sqlalchemy"` succeeds.

**Validation**: `uv sync` succeeds. All directories exist. `pyproject.toml` is valid.

---

## Agent 1: Configuration System

**Goal**: Implement YAML config loading with Pydantic validation, fail-fast on startup.

**Prerequisites**: Agent 0.

**Files to create/modify**:
- `src/app/config/schema.py`
- `src/app/config/loader.py`
- `src/app/config/__init__.py`

**Tasks**:
1. **`schema.py`**: Define Pydantic v2 `BaseModel` classes:
   - `ServerConfig(host: str, port: int, debug: bool)`
   - `DatabaseConfig(url: str, echo: bool)` — validate URL starts with valid SQLAlchemy async scheme
   - `AuthConfig(api_key: str)` — `min_length=8`
   - `LoggingConfig(level: Literal["DEBUG","INFO","WARNING","ERROR","CRITICAL"], format: Literal["json","console"], file: Optional[str])`
   - `ScheduledBackupConfig(enabled: bool, frequency_hours: PositiveInt)`
   - `BackupConfig(enabled: bool, directory: str, scheduled: ScheduledBackupConfig, max_backups: PositiveInt)`
   - `PaginationConfig(default_page_size: PositiveInt, max_page_size: PositiveInt)` — validator: `default_page_size <= max_page_size`
   - `AppConfig(server: ServerConfig, database: DatabaseConfig, auth: AuthConfig, logging: LoggingConfig, backup: BackupConfig, pagination: PaginationConfig)`

2. **`loader.py`**: Implement `load_config(path: str | None = None) -> AppConfig`:
   - Default path from env var `CONFIG_PATH` or `"config.yaml"`.
   - Read YAML with `yaml.safe_load`.
   - Parse into `AppConfig` — Pydantic raises `ValidationError` with clear messages.
   - Log (print at this stage) success with loaded config summary (masking api_key).
   - Raise `SystemExit(1)` on any error with descriptive message.

3. **`__init__.py`**: Export `AppConfig`, `load_config`.

**Outputs**: `load_config()` returns a fully validated `AppConfig` object, or the process exits.

**Validation**: Write a quick smoke test (manual or inline script) that loads `config.example.yaml` — it should fail on `"CHANGE-ME-TO-A-SECURE-KEY"` only if you add a validator blocking default values (optional). It should succeed with a modified copy.

---

## Agent 2: Domain Layer

**Goal**: Define all domain entities, enums, exceptions, and repository interfaces (protocols).

**Prerequisites**: Agent 0.

**Files to create/modify**:
- `src/app/domain/enums.py`
- `src/app/domain/exceptions.py`
- `src/app/domain/entities/common.py`
- `src/app/domain/entities/exercise.py`
- `src/app/domain/entities/muscle_group.py`
- `src/app/domain/entities/routine.py`
- `src/app/domain/entities/mesocycle.py`
- `src/app/domain/entities/session.py`
- `src/app/domain/entities/bodyweight.py`
- `src/app/domain/repositories/base.py`
- `src/app/domain/repositories/exercise.py`
- `src/app/domain/repositories/muscle_group.py`
- `src/app/domain/repositories/routine.py`
- `src/app/domain/repositories/mesocycle.py`
- `src/app/domain/repositories/session.py`
- `src/app/domain/repositories/bodyweight.py`
- `src/app/application/interfaces/unit_of_work.py`

**Tasks**:
1. **`enums.py`**: Define enums using `enum.Enum`:
   - `SetType: standard, dropset`
   - `SessionStatus: planned, in_progress, completed`
   - `WeekType: training, deload`
   - `MesocycleStatus: planned, active, completed`
   - `MuscleRole: primary, secondary`

2. **`exceptions.py`**: Define exception hierarchy:
   - `DomainException(Exception)` — base
   - `EntityNotFoundException(DomainException)` — entity_type, entity_id
   - `ReferentialIntegrityException(DomainException)` — entity_type, entity_id, referenced_by
   - `InvalidStateTransitionException(DomainException)` — from_state, to_state
   - `ValidationException(DomainException)` — field, message

3. **`entities/common.py`**: Define base `Entity` dataclass with `id: UUID`, `created_at: datetime`, `updated_at: datetime`. All entities are plain Python `dataclass` or `@dataclass` with slots. NO SQLAlchemy dependency here.

4. **Entity files**: Define dataclasses mirroring DESIGN.md Section 3.2 tables. Include type hints. Use `Optional` where nullable. Use `list[ChildEntity]` for relationships (e.g., `Routine.exercises: list[RoutineExercise]`).

5. **`repositories/base.py`**: Define `AbstractRepository(Protocol[T])` with:
   - `async get_by_id(id: UUID) -> T | None`
   - `async get_all(offset: int, limit: int) -> tuple[list[T], int]` (items + total count)
   - `async add(entity: T) -> T`
   - `async update(entity: T) -> T`
   - `async delete(id: UUID) -> bool`

6. **Repository interfaces**: Each extends `AbstractRepository` with entity-specific methods:
   - `ExerciseRepository`: `get_by_name`, `get_by_muscle_group`, `has_references(id) -> bool`
   - `RoutineRepository`: `get_with_exercises(id)`, `has_references(id) -> bool`
   - `MesocycleRepository`: `get_with_weeks(id)`, `get_active() -> Mesocycle | None`, `has_references(id) -> bool`
   - `SessionRepository`: `get_by_date_range`, `get_by_mesocycle`, `get_by_status`, `get_for_date(date) -> list[Session]`
   - `BodyweightRepository`: `get_by_date_range`, `get_latest() -> BodyweightLog | None`

7. **`unit_of_work.py`**: Define `AbstractUnitOfWork(ABC)` with:
   - Properties for each repository
   - `async commit()`
   - `async rollback()`
   - `async __aenter__` / `async __aexit__`

**Outputs**: All domain types importable. No external dependencies (only stdlib + typing).

**Validation**: `uv run python -c "from app.domain.entities.exercise import Exercise; from app.domain.enums import SetType"` succeeds.

---

## Agent 3: Infrastructure — Database Models & Connection

**Goal**: Implement SQLAlchemy 2.0 async models and database connection factory.

**Prerequisites**: Agent 1, Agent 2.

**Files to create/modify**:
- `src/app/infrastructure/database/__init__.py`
- `src/app/infrastructure/database/connection.py`
- `src/app/infrastructure/database/models/base.py`
- `src/app/infrastructure/database/models/exercise.py`
- `src/app/infrastructure/database/models/muscle_group.py`
- `src/app/infrastructure/database/models/routine.py`
- `src/app/infrastructure/database/models/mesocycle.py`
- `src/app/infrastructure/database/models/session.py`
- `src/app/infrastructure/database/models/bodyweight.py`
- `src/app/infrastructure/seed.py`
- `alembic/env.py` (complete)
- `alembic/versions/001_initial.py`

**Tasks**:
1. **`models/base.py`**:
   - `Base = DeclarativeBase` with `MappedAsDataclass` mixin or standard mapped_column approach.
   - `UUIDPrimaryKeyMixin`: `id: Mapped[str]` as UUID stored as CHAR(36) (SQLite compat), default `uuid4()`.
   - `TimestampMixin`: `created_at`, `updated_at` as `Mapped[datetime]` with UTC defaults and onupdate.

2. **Model files**: Implement all tables from DESIGN.md Section 3.2 using SQLAlchemy 2.0 `Mapped[]`, `mapped_column()`, `relationship()`.
   - Use string enum columns (SQLite compat).
   - Define `__tablename__` matching the design.
   - Use `ForeignKey` with appropriate `ondelete` (`CASCADE` or `RESTRICT` per DESIGN.md Section 3.3).
   - `relationship()` with `lazy="selectin"` for commonly needed joins, `lazy="noload"` otherwise.
   - Unique constraints and indexes as specified.

3. **`connection.py`**:
   - `init_engine(config: DatabaseConfig) -> AsyncEngine`
   - `init_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]`
   - `init_db(engine: AsyncEngine)` — creates tables (for testing) or runs alembic (for prod).
   - Handle SQLite-specific pragmas (`journal_mode=WAL`, `foreign_keys=ON`) via event listeners.

4. **`seed.py`**: `async seed_muscle_groups(session: AsyncSession)` — inserts all muscle groups from DESIGN.md Section 3.2 if not present. Idempotent.

5. **Alembic**:
   - Complete `env.py` to use async engine from app config.
   - Generate `001_initial.py` migration (or write it manually matching the models).

**Outputs**: All models importable, `create_all` creates correct schema, alembic migrations work.

**Validation**: Write inline script: create in-memory SQLite, `create_all`, insert a muscle group, query it back.

---

## Agent 4: Infrastructure — Repositories & Unit of Work

**Goal**: Implement concrete SQLAlchemy repositories and the Unit of Work pattern.

**Prerequisites**: Agent 2, Agent 3.

**Files to create/modify**:
- `src/app/infrastructure/database/repositories/base.py`
- `src/app/infrastructure/database/repositories/exercise.py`
- `src/app/infrastructure/database/repositories/muscle_group.py`
- `src/app/infrastructure/database/repositories/routine.py`
- `src/app/infrastructure/database/repositories/mesocycle.py`
- `src/app/infrastructure/database/repositories/session.py`
- `src/app/infrastructure/database/repositories/bodyweight.py`
- `src/app/infrastructure/unit_of_work.py`

**Tasks**:
1. **`repositories/base.py`**: Implement `SqlAlchemyRepository(Generic[ModelT, EntityT])`:
   - Constructor takes `AsyncSession`.
   - `get_by_id`: `session.get(ModelT, id)` + convert to entity.
   - `get_all`: `select(ModelT).offset().limit()` + `select(func.count())`.
   - `add`: construct model from entity, `session.add()`, `session.flush()`, return entity.
   - `update`: merge, flush, return entity.
   - `delete`: get, `session.delete()`, flush.
   - Private `_to_entity(model) -> EntityT` and `_to_model(entity) -> ModelT` mapper methods (overridden per repo).

2. **Entity-specific repositories**: Extend base with:
   - Custom query methods (e.g., `get_by_name`, `get_by_date_range`).
   - `has_references` methods using `exists()` subqueries on referencing tables.
   - Eager loading strategies for joined queries (e.g., `get_with_exercises` loads routine + exercises + sets).

3. **`unit_of_work.py`**: `SqlAlchemyUnitOfWork` implementing `AbstractUnitOfWork`:
   - Holds `AsyncSession`.
   - Lazily creates repository instances on property access.
   - `commit()` calls `session.commit()`.
   - `rollback()` calls `session.rollback()`.
   - Context manager handles session lifecycle.

**Outputs**: All CRUD operations work through repositories. UoW wraps transactions.

**Validation**: Import and type-check all repositories. No runtime test yet (covered by Agent 12/13).

---

## Agent 5: Application — Services (Core CRUD)

**Goal**: Implement service layer for all core CRUD operations with business rule enforcement.

**Prerequisites**: Agent 2, Agent 4.

**Files to create/modify**:
- `src/app/application/dto/pagination.py`
- `src/app/application/dto/exercise.py`
- `src/app/application/dto/routine.py`
- `src/app/application/dto/mesocycle.py`
- `src/app/application/dto/session.py`
- `src/app/application/dto/bodyweight.py`
- `src/app/application/services/exercise_service.py`
- `src/app/application/services/muscle_group_service.py`
- `src/app/application/services/routine_service.py`
- `src/app/application/services/mesocycle_service.py`
- `src/app/application/services/session_service.py`
- `src/app/application/services/bodyweight_service.py`

**Tasks**:
1. **DTOs** (`application/dto/`):
   - `PaginationInput(page: int = 1, page_size: int = 20)` — Pydantic model with validators.
   - `PaginatedResult(Generic[T]): items, total, page, page_size, total_pages`.
   - Create/Update DTOs for each entity (Pydantic models with validation).

2. **`exercise_service.py`**: `ExerciseService`:
   - Constructor: `__init__(self, uow: AbstractUnitOfWork)`
   - `create_exercise(dto: CreateExerciseDTO) -> Exercise` — validate unique name, create, commit.
   - `update_exercise(id, dto) -> Exercise` — fetch, update fields, commit.
   - `delete_exercise(id) -> bool` — check `has_references`, raise `ReferentialIntegrityException` if true, else delete.
   - `get_exercise(id) -> Exercise` — raise `EntityNotFoundException` if missing.
   - `list_exercises(pagination, muscle_group_id?) -> PaginatedResult[Exercise]`
   - `assign_muscle_groups(exercise_id, assignments: list[MuscleGroupAssignment]) -> Exercise`

3. **`muscle_group_service.py`**: Read-only (muscle groups are seeded). `list_all() -> list[MuscleGroup]`.

4. **`routine_service.py`**: `RoutineService`:
   - Full CRUD on routines, routine_exercises, routine_sets.
   - `create_routine` with nested exercises and sets in one call.
   - `add_routine_exercise`, `remove_routine_exercise` (reorders remaining).
   - `add_routine_set`, `remove_routine_set` (renumbers remaining).
   - Delete routine: check references in planned_session and session tables.

5. **`mesocycle_service.py`**: `MesocycleService`:
   - CRUD on mesocycles, weeks, planned_sessions.
   - Validate week date ranges don't overlap.
   - Validate only one `active` mesocycle at a time.
   - Delete mesocycle: check references in session table.

6. **`session_service.py`**: `SessionService`:
   - `create_session(dto)`: if `routine_id` provided, copy routine structure into session_exercises/session_sets. If `planned_session_id` provided, link to it.
   - `start_session(id)`: validate status is `planned`, set `started_at`, status → `in_progress`.
   - `complete_session(id)`: validate status is `in_progress`, set `completed_at`, status → `completed`.
   - `update_session(id, dto)`: allow editing `started_at`, `completed_at`, `notes`, `status` (with transition validation).
   - `log_set_result(set_id, dto)`: update `actual_reps`, `actual_rir`, `actual_weight_kg`, `performed_at`.
   - CRUD for session_exercises and session_sets.
   - Delete session: cascade handled by DB.

7. **`bodyweight_service.py`**: `BodyweightService`:
   - Simple CRUD. `list` supports date range filtering.

**Outputs**: All services importable, all methods implemented with proper error handling and UoW transaction management.

**Validation**: Type-checking passes. Method signatures match the GraphQL mutation/query catalog from DESIGN.md.

---

## Agent 6: Application — Services (Insights & Calendar)

**Goal**: Implement insight and calendar services for training analytics.

**Prerequisites**: Agent 5.

**Files to create/modify**:
- `src/app/application/dto/insight.py`
- `src/app/application/services/insight_service.py`
- `src/app/application/services/calendar_service.py`

**Tasks**:
1. **`dto/insight.py`**: Define:
   - `WeeklyVolume(week_number, muscle_group, total_sets)`
   - `MuscleGroupVolume(muscle_group, total_sets, percentage)`
   - `VolumeInsight(mesocycle_id, weekly_volumes, total_sets, muscle_group_breakdown)`
   - `IntensityInsight(mesocycle_id, weekly_avg_rir, weekly_avg_rpe)`
   - `WeeklyExerciseProgress(week_number, max_weight_kg, avg_reps, avg_rir, estimated_1rm)`
   - `ProgressiveOverloadInsight(exercise_id, mesocycle_id, weekly_progress, e1rm_progression)`
   - `ExerciseHistoryEntry(session_date, sets: list[SetSummary])`
   - `CalendarDay(date, planned_session, session, is_completed, is_rest_day)`

2. **`insight_service.py`**: `InsightService`:
   - `get_volume_insight(mesocycle_id, muscle_group_id?)`:
     - Fetch all sessions in mesocycle → session_exercises → session_sets (only completed sets).
     - Join with exercise_muscle_group to map sets to muscle groups.
     - Aggregate by week_number and muscle_group.
   - `get_intensity_insight(mesocycle_id)`:
     - Average `actual_rir` per week across all completed sets.
   - `get_progressive_overload_insight(mesocycle_id, exercise_id)`:
     - Per-week: max weight, avg reps, avg RIR for that exercise.
     - Calculate estimated 1RM via Epley: `weight × (1 + reps/30)`.
     - Return progression array.
   - `get_exercise_history(exercise_id, pagination)`:
     - All session_sets for this exercise across all sessions, grouped by session date.

3. **`calendar_service.py`**: `CalendarService`:
   - `get_calendar_day(date: date) -> CalendarDay`:
     - Check `planned_session` for that date (from active mesocycle).
     - Check `session` for that date.
     - Determine `is_completed` (session exists and status = completed).
     - Determine `is_rest_day` (no planned session or planned session with null routine).
   - `get_calendar_range(start_date, end_date) -> list[CalendarDay]`:
     - Batch query for efficiency.

**Outputs**: Insight calculations correct, calendar logic handles all edge cases.

**Validation**: Logic manually reviewed. Formulas verified (Epley formula).

---

## Agent 7: Presentation — GraphQL Types & Inputs

**Goal**: Define all Strawberry GraphQL types and input types (code-first schema).

**Prerequisites**: Agent 2, Agent 5, Agent 6 (for DTO shapes).

**Files to create/modify**:
- `src/app/presentation/graphql/types/pagination.py`
- `src/app/presentation/graphql/types/exercise.py`
- `src/app/presentation/graphql/types/muscle_group.py`
- `src/app/presentation/graphql/types/routine.py`
- `src/app/presentation/graphql/types/mesocycle.py`
- `src/app/presentation/graphql/types/session.py`
- `src/app/presentation/graphql/types/bodyweight.py`
- `src/app/presentation/graphql/types/insight.py`
- `src/app/presentation/graphql/types/calendar.py`
- `src/app/presentation/graphql/inputs/pagination.py`
- `src/app/presentation/graphql/inputs/exercise.py`
- `src/app/presentation/graphql/inputs/routine.py`
- `src/app/presentation/graphql/inputs/mesocycle.py`
- `src/app/presentation/graphql/inputs/session.py`
- `src/app/presentation/graphql/inputs/bodyweight.py`

**Tasks**:
1. **Types** (`@strawberry.type`): Map every entity and DTO to a Strawberry type.
   - Use `strawberry.ID` for UUIDs.
   - Use `datetime.datetime` and `datetime.date` scalars.
   - Use `strawberry.enum` for enums.
   - `PaginatedExercises`, `PaginatedRoutines`, etc. using generic pattern or explicit types.
   - Nested types (e.g., `RoutineType` has `exercises: list[RoutineExerciseType]`).
   - All fields documented with `strawberry.field(description="...")`.

2. **Inputs** (`@strawberry.input`): Map every create/update operation to an input type.
   - Use `Optional` for nullable/optional fields.
   - `PaginationInput(page: int = 1, pageSize: int = 20)`.
   - `CreateExerciseInput(name: str, description: Optional[str], equipment: Optional[str], muscleGroups: Optional[list[MuscleGroupAssignmentInput]])`.
   - `LogSetResultInput(actualReps: int, actualRir: int, actualWeightKg: float, performedAt: Optional[datetime])`.
   - Follow camelCase for GraphQL convention; use `strawberry.field(name="camelCase")` or configure Strawberry's naming convention.

3. **Converter functions**: In each type file, add `@staticmethod from_entity(entity) -> Type` methods for converting domain entities to GraphQL types.

**Outputs**: All GraphQL types and inputs defined, importable, and properly documented.

**Validation**: `uv run python -c "from app.presentation.graphql.types.exercise import ExerciseType"` succeeds. Schema can be printed.

---

## Agent 8: Presentation — Resolvers & Mutations

**Goal**: Implement all GraphQL resolvers (queries) and mutations, wiring them to services.

**Prerequisites**: Agent 5, Agent 6, Agent 7.

**Files to create/modify**:
- `src/app/presentation/graphql/context.py`
- `src/app/presentation/graphql/resolvers/exercise.py`
- `src/app/presentation/graphql/resolvers/muscle_group.py`
- `src/app/presentation/graphql/resolvers/routine.py`
- `src/app/presentation/graphql/resolvers/mesocycle.py`
- `src/app/presentation/graphql/resolvers/session.py`
- `src/app/presentation/graphql/resolvers/bodyweight.py`
- `src/app/presentation/graphql/resolvers/insight.py`
- `src/app/presentation/graphql/resolvers/calendar.py`
- `src/app/presentation/graphql/resolvers/backup.py`
- `src/app/presentation/graphql/mutations/exercise.py`
- `src/app/presentation/graphql/mutations/routine.py`
- `src/app/presentation/graphql/mutations/mesocycle.py`
- `src/app/presentation/graphql/mutations/session.py`
- `src/app/presentation/graphql/mutations/bodyweight.py`
- `src/app/presentation/graphql/mutations/backup.py`
- `src/app/presentation/graphql/schema.py`

**Tasks**:
1. **`context.py`**: Define `GraphQLContext` dataclass holding all services. Define `get_context` dependency that builds context from FastAPI's DI.

2. **Resolvers**: Each file defines functions decorated with resolver patterns:
   ```python
   async def resolve_exercises(
       info: strawberry.types.Info,
       pagination: Optional[PaginationInput] = None,
       muscle_group_id: Optional[strawberry.ID] = None
   ) -> PaginatedExercisesType:
       service = info.context.exercise_service
       result = await service.list_exercises(...)
       return PaginatedExercisesType.from_paginated_result(result)
   ```

3. **Mutations**: Each file defines mutation functions:
   ```python
   async def create_exercise(
       info: strawberry.types.Info,
       input: CreateExerciseInput
   ) -> ExerciseType:
       service = info.context.exercise_service
       exercise = await service.create_exercise(input.to_dto())
       return ExerciseType.from_entity(exercise)
   ```
   - Error handling: catch domain exceptions, re-raise as `strawberry.exceptions` or return union error types.

4. **`schema.py`**: Assemble `Query` and `Mutation` classes:
   ```python
   @strawberry.type
   class Query:
       exercises = strawberry.field(resolver=resolve_exercises)
       exercise = strawberry.field(resolver=resolve_exercise)
       # ... all queries

   @strawberry.type
   class Mutation:
       create_exercise = strawberry.mutation(resolver=create_exercise)
       # ... all mutations

   schema = strawberry.Schema(query=Query, mutation=Mutation)
   ```

**Outputs**: Complete GraphQL schema with all queries and mutations wired to services.

**Validation**: `schema.as_str()` produces valid GraphQL SDL matching DESIGN.md Section 6.

---

## Agent 9: Presentation — Middleware & Auth

**Goal**: Implement authentication middleware, logging middleware, and error handling.

**Prerequisites**: Agent 1.

**Files to create/modify**:
- `src/app/presentation/middleware/auth.py`
- `src/app/presentation/middleware/logging.py`
- `src/app/presentation/middleware/error_handler.py`
- `src/app/presentation/rest/health.py`

**Tasks**:
1. **`auth.py`**: FastAPI middleware:
   - Skip `/health` endpoint.
   - Extract `Authorization: Bearer <token>` header.
   - Compare against `config.auth.api_key`.
   - On mismatch: return `401` JSON response.
   - On match: continue to next middleware.

2. **`logging.py`**: FastAPI middleware:
   - Generate `request_id` UUID per request, bind to structlog context.
   - Log request start: method, path, request_id.
   - Log request end: status_code, duration_ms, request_id.
   - Use `structlog.get_logger()`.

3. **`error_handler.py`**: Exception handler:
   - Catch `DomainException` subtypes and map to GraphQL error extensions.
   - `EntityNotFoundException` → `NOT_FOUND`
   - `ReferentialIntegrityException` → `CONFLICT`
   - `InvalidStateTransitionException` → `VALIDATION_ERROR`
   - `ValidationException` → `VALIDATION_ERROR`
   - Unhandled exceptions → `INTERNAL_ERROR` + log full traceback.

4. **`rest/health.py`**: FastAPI router:
   - `GET /health` → `{"status": "healthy", "version": "1.0.0"}`.
   - No auth required.

5. **Structlog setup**: Create initialization function called at app startup:
   - Configure processors based on `config.logging.format`.
   - Set log level from `config.logging.level`.
   - Optionally add file handler from `config.logging.file`.

**Outputs**: All middleware functional. Health endpoint responds. Logging structured.

**Validation**: Manual test: request without API key → 401. With key → passes through.

---

## Agent 10: App Assembly & DI Wiring

**Goal**: Wire everything together in the FastAPI application factory.

**Prerequisites**: Agent 1–9.

**Files to create/modify**:
- `src/app/main.py`
- `src/app/dependencies.py`

**Tasks**:
1. **`dependencies.py`**:
   - `get_config() -> AppConfig` (singleton, loaded once).
   - `get_engine() -> AsyncEngine` (singleton).
   - `get_session_factory() -> async_sessionmaker` (singleton).
   - `get_db_session() -> AsyncGenerator[AsyncSession, None]` (per-request).
   - `get_unit_of_work(session) -> SqlAlchemyUnitOfWork`.
   - One provider per service: `get_exercise_service(uow) -> ExerciseService`, etc.
   - `get_graphql_context(request, ...)` — builds `GraphQLContext` with all services.

2. **`main.py`**: `create_app() -> FastAPI`:
   - Load config.
   - Configure structlog.
   - Create engine and session factory.
   - Run seed (muscle groups) on startup event.
   - Run alembic migrations on startup (optional, configurable).
   - Add middleware: auth, logging, CORS (optional).
   - Mount REST router (`/health`).
   - Mount Strawberry GraphQL app at `/graphql` with context dependency.
   - Start backup scheduler if configured.
   - Return app.
   - Add shutdown event: dispose engine, stop scheduler.

**Outputs**: `uvicorn app.main:create_app --factory` starts the full application.

**Validation**: App starts, `/health` returns 200, `/graphql` responds to introspection (with valid API key).

---

## Agent 11: Backup System

**Goal**: Implement manual and scheduled backup functionality.

**Prerequisites**: Agent 1, Agent 10.

**Files to create/modify**:
- `src/app/infrastructure/backup/manager.py`
- `src/app/infrastructure/backup/scheduler.py`
- `src/app/application/services/backup_service.py`

**Tasks**:
1. **`manager.py`**: `BackupManager`:
   - Constructor: `__init__(self, db_url: str, backup_dir: str, max_backups: int)`
   - `async create_backup() -> BackupResult`:
     - Parse DB URL; if SQLite, get file path.
     - Execute `PRAGMA wal_checkpoint(FULL)` via raw connection.
     - Copy file with `shutil.copy2` to `backup_dir/backup_YYYYMMDD_HHMMSS.db`.
     - Return `BackupResult(success=True, filename, size_bytes, created_at)`.
   - `rotate_backups()`: list backup files sorted by date, delete oldest if count > `max_backups`.
   - Non-SQLite: raise `NotImplementedError` with clear message.

2. **`scheduler.py`**: `BackupScheduler`:
   - Uses `APScheduler.AsyncIOScheduler`.
   - `start(frequency_hours, backup_manager)`: adds interval job.
   - `stop()`: shuts down scheduler gracefully.

3. **`backup_service.py`**: `BackupService`:
   - `trigger_backup() -> BackupResult`: calls `backup_manager.create_backup()` + `rotate_backups()`.
   - Used by GraphQL mutation and scheduler.

4. Wire into `main.py`: start scheduler on startup if `config.backup.scheduled.enabled`.

**Outputs**: Manual backup via GraphQL works. Scheduled backup runs on interval.

**Validation**: Trigger backup mutation → file appears in `backups/` directory.

---

## Agent 12: Unit Tests

**Goal**: Comprehensive unit tests for all service layer methods with mocked dependencies.

**Prerequisites**: Agent 5, Agent 6, Agent 11.

**Files to create/modify**:
- `tests/conftest.py` (shared fixtures)
- `tests/factories/*.py` (all factory files)
- `tests/unit/test_exercise_service.py`
- `tests/unit/test_muscle_group_service.py`
- `tests/unit/test_routine_service.py`
- `tests/unit/test_mesocycle_service.py`
- `tests/unit/test_session_service.py`
- `tests/unit/test_bodyweight_service.py`
- `tests/unit/test_insight_service.py`
- `tests/unit/test_calendar_service.py`
- `tests/unit/test_backup_service.py`
- `tests/unit/test_config_validation.py`

**Tasks**:
1. **`conftest.py`**:
   - Fixture: `mock_uow` — `AsyncMock` implementing `AbstractUnitOfWork` with mocked repository properties.
   - Fixture: `app_config` — valid `AppConfig` for testing.
   - Configure `pytest-asyncio` mode (`auto`).

2. **Factories**: `factory-boy` factories for all domain entities with sensible defaults:
   - `ExerciseFactory`, `RoutineFactory` (with nested exercises/sets), `MesocycleFactory`, `SessionFactory`, `BodyweightLogFactory`.

3. **Test files** (each service):
   - **Happy path**: All CRUD operations return expected results.
   - **Not found**: Operations on non-existent IDs raise `EntityNotFoundException`.
   - **Referential integrity**: Delete blocked when references exist.
   - **Validation**: Invalid inputs raise `ValidationException`.
   - **State transitions** (sessions): invalid transitions raise `InvalidStateTransitionException`.
   - **Pagination**: correct offset/limit calculation.
   - Mock setup: `mock_uow.exercise_repo.get_by_id.return_value = ExerciseFactory()` etc.

4. **`test_insight_service.py`**:
   - Mock session data with known values.
   - Verify volume calculation: correct set counting per muscle group.
   - Verify intensity calculation: correct RIR averaging.
   - Verify progressive overload: correct 1RM calculation and progression.

5. **`test_config_validation.py`**:
   - Valid config loads successfully.
   - Missing required fields → `ValidationError`.
   - Invalid types → `ValidationError`.
   - `default_page_size > max_page_size` → `ValidationError`.
   - Invalid log level → `ValidationError`.

**Outputs**: All unit tests pass. Coverage ≥ 85% on `application/services/`.

**Validation**: `uv run pytest tests/unit/ -v --cov=app.application --cov-report=term-missing`

---

## Agent 13: Integration Tests

**Goal**: End-to-end tests via GraphQL against a real (in-memory) database.

**Prerequisites**: Agent 10, Agent 12.

**Files to create/modify**:
- `tests/conftest.py` (add integration fixtures)
- `tests/integration/test_exercise_api.py`
- `tests/integration/test_routine_api.py`
- `tests/integration/test_mesocycle_api.py`
- `tests/integration/test_session_api.py`
- `tests/integration/test_bodyweight_api.py`
- `tests/integration/test_insight_api.py`
- `tests/integration/test_calendar_api.py`
- `tests/integration/test_backup_api.py`
- `tests/integration/test_auth.py`

**Tasks**:
1. **Integration fixtures in `conftest.py`**:
   ```python
   @pytest.fixture(scope="session")
   async def engine():
       engine = create_async_engine("sqlite+aiosqlite://", echo=True)
       async with engine.begin() as conn:
           await conn.run_sync(Base.metadata.create_all)
       yield engine
       await engine.dispose()

   @pytest.fixture
   async def db_session(engine):
       async with async_sessionmaker(engine)() as session:
           async with session.begin():
               yield session
           await session.rollback()  # clean state per test

   @pytest.fixture
   async def client(engine, db_session):
       # Override dependencies to use test session
       app = create_app()
       app.dependency_overrides[get_db_session] = lambda: db_session
       async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
           c.headers["Authorization"] = f"Bearer {TEST_API_KEY}"
           yield c
   ```

2. **GraphQL helper**: Utility function `async graphql_request(client, query, variables=None) -> dict` that POSTs to `/graphql` and returns parsed JSON.

3. **Test files**: Each file tests full CRUD cycles via GraphQL:
   - **`test_exercise_api.py`**:
     - Create exercise → query it → update it → list all → delete it → confirm gone.
     - Create with muscle groups → verify associations.
     - Delete exercise referenced by routine → expect error.
   - **`test_routine_api.py`**:
     - Create routine with exercises and sets (including supersets and dropsets).
     - Add/remove exercises and sets.
     - Verify ordering.
   - **`test_mesocycle_api.py`**:
     - Create mesocycle with weeks (training + deload) and planned sessions.
     - Verify date validations.
   - **`test_session_api.py`**:
     - Create session from routine → verify copied structure.
     - Start → log set results → complete. Verify state transitions.
     - Create ad-hoc session with custom exercises/sets.
     - Invalid state transition → error.
   - **`test_bodyweight_api.py`**: CRUD + date range filtering.
   - **`test_insight_api.py`**:
     - Seed a mesocycle with sessions and logged sets.
     - Query volume insight → verify numbers.
     - Query progressive overload → verify calculation.
   - **`test_calendar_api.py`**:
     - Seed planned sessions → query calendar day → verify response.
     - Query range → verify all days returned.
   - **`test_backup_api.py`**:
     - Trigger backup → verify file created (using `tmp_path` fixture for backup dir).
   - **`test_auth.py`**:
     - Request without API key → 401.
     - Request with wrong API key → 401.
     - Request with correct API key → passes.
     - Health endpoint without key → 200 (no auth required).

**Outputs**: All integration tests pass. Full API coverage.

**Validation**: `uv run pytest tests/integration/ -v`

---

## Agent 14: Docker & Final Polish

**Goal**: Finalize Dockerfile, documentation, and ensure everything works end-to-end.

**Prerequisites**: All previous agents.

**Files to create/modify**:
- `Dockerfile`
- `docker-compose.yml`
- `README.md`
- `.dockerignore`
- `pyproject.toml` (final scripts section)

**Tasks**:
1. **`Dockerfile`**: Implement as specified in DESIGN.md Section 10.
   - Multi-stage: base → test (runs all tests, fails build on failure) → production.
   - Use `uv` for package management inside Docker.

2. **`docker-compose.yml`**:
   ```yaml
   services:
     api:
       build:
         context: .
         target: production
       ports:
         - "8000:8000"
       volumes:
         - ./config.yaml:/app/config.yaml:ro
         - ./data:/app/data
         - ./backups:/app/backups
       environment:
         - CONFIG_PATH=/app/config.yaml
   ```

3. **`.dockerignore`**: Standard Python + `.git`, `__pycache__`, `*.db`, `.venv`, `backups/`, `data/`.

4. **`pyproject.toml` scripts**:
   ```toml
   [project.scripts]
   serve = "uvicorn app.main:create_app --factory"

   [tool.pytest.ini_options]
   asyncio_mode = "auto"
   testpaths = ["tests"]
   markers = ["unit", "integration"]

   [tool.ruff]
   line-length = 100
   target-version = "py312"
   ```

5. **`README.md`**: Comprehensive documentation:
   - Project overview.
   - Quick start (local + Docker).
   - Configuration reference.
   - API usage examples (GraphQL queries/mutations).
   - Development setup.
   - Testing instructions.
   - Backup management.

6. **Final validation**:
   - `uv run ruff check src/ tests/` — no errors.
   - `uv run pytest tests/ -v --cov=app --cov-report=term-missing` — all pass, ≥80% coverage.
   - `docker build -t workout-tracker .` — succeeds (tests pass in build).
   - `docker compose up` → app starts → `/health` returns 200 → GraphQL introspection works.

**Outputs**: Production-ready Docker image. Complete documentation. All tests pass.

---

## Agent Execution Summary

| Agent | Name | Est. Complexity | Key Output |
|---|---|---|---|
| 0 | Project Scaffold | Low | Project structure, dependencies |
| 1 | Configuration System | Low | Config loading + validation |
| 2 | Domain Layer | Medium | Entities, enums, interfaces |
| 3 | DB Models & Connection | Medium | SQLAlchemy models, migrations |
| 4 | Repositories & UoW | Medium | Data access layer |
| 5 | Core CRUD Services | High | Business logic for all entities |
| 6 | Insights & Calendar | Medium | Analytics + calendar services |
| 7 | GraphQL Types & Inputs | Medium | Code-first schema types |
| 8 | Resolvers & Mutations | High | Full GraphQL API wiring |
| 9 | Middleware & Auth | Low | Security, logging, errors |
| 10 | App Assembly | Medium | Working application |
| 11 | Backup System | Low | Backup + scheduling |
| 12 | Unit Tests | High | Service layer tests |
| 13 | Integration Tests | High | End-to-end API tests |
| 14 | Docker & Polish | Low | Production deployment |

---

## Conventions for All Agents

1. **Python version**: 3.12+. Use modern syntax (`type` aliases, `|` union, `match` where appropriate).
2. **Async everywhere**: All database operations, service methods, and resolvers are `async`.
3. **Type hints**: 100% coverage. Use `typing` module where needed.
4. **Docstrings**: Google style on all public classes and methods.
5. **Error messages**: Human-readable, include entity type and ID where applicable.
6. **Imports**: Absolute imports from `app.` prefix. No circular imports (enforced by layer boundaries).
7. **No hardcoded values**: All configurable values from `AppConfig`.
8. **UTC timestamps**: Always use `datetime.now(UTC)`. Never use naive datetimes.
9. **Naming**: snake_case for Python, camelCase for GraphQL fields.
10. **Commit granularity**: Each agent's work is one logical commit with a descriptive message.