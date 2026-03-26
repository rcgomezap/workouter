# Task 05: Personal Records System

**Phase**: 2 - Enhanced Analytics Core  
**Estimated Time**: 2-3 days  
**Priority**: High  
**Status**: Ready for Implementation

---

## User Story

**As a** user  
**I want to** view my personal records for each exercise  
**So that** I can track my all-time best performances and stay motivated

---

## Background

Currently, the API tracks workout history but doesn't explicitly identify or store "Personal Records" (PRs). Users have to manually search through history to find their best lifts. A dedicated PR system is essential for a strength training app to visualize progress.

We need to track four specific types of records:
1. **Max Weight**: The heaviest weight lifted for a single rep (or any rep count).
2. **Max Volume**: The highest total volume (sets × reps × weight) in a single session.
3. **Max Reps at Weight**: The most reps performed at specific weight milestones (e.g., 60kg, 100kg).
4. **Estimated 1RM**: The highest estimated one-rep max using the Epley formula.

---

## Acceptance Criteria

### Functional Requirements
- [ ] Calculate and return **Max Weight** PR for a specific exercise
- [ ] Calculate and return **Max Volume** (single session) PR
- [ ] Calculate and return **Estimated 1RM** PR
- [ ] Calculate and return **Max Reps** records for top 5 weight increments
- [ ] Query for **Recent PRs** across all exercises (e.g., last 10 records)
- [ ] PRs must be based on **Completed** sessions only

### Technical Requirements
- [ ] Implement `PersonalRecordDTO` and `ExercisePersonalRecordsDTO`
- [ ] Add efficient repository queries to fetch necessary session data
- [ ] Implement calculation logic in `InsightService`
- [ ] Expose data via GraphQL `exercisePersonalRecords` and `recentPersonalRecords` queries
- [ ] Performance: PR calculations should take <200ms for an exercise with <500 sessions

### Testing Requirements
- [ ] Unit tests for all calculation logic (max weight, volume, 1RM)
- [ ] Integration tests with realistic workout history
- [ ] GraphQL API tests verifying correct schema and data return

---

## Implementation Plan

### Step 1: Create DTOs

**File**: `src/app/application/dto/insight.py`

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class PersonalRecordDTO:
    exercise_id: UUID
    exercise_name: str
    record_type: str  # "max_weight", "max_volume", "max_reps_at_weight", "estimated_1rm"
    value: float
    recorded_at: datetime
    session_id: UUID
    details: dict  # e.g., {weight: 100, reps: 10, sets: 3}

@dataclass
class ExercisePersonalRecordsDTO:
    exercise_id: UUID
    exercise_name: str
    max_weight: PersonalRecordDTO | None
    max_volume_single_session: PersonalRecordDTO | None
    max_reps_at_weight: list[PersonalRecordDTO]  # Top 5 by weight
    estimated_one_rep_max: PersonalRecordDTO | None
```

### Step 2: Add Repository Methods

**File**: `src/app/infrastructure/database/repositories/session.py`

We need to efficiently fetch completed sessions for an exercise. We can reuse the existing `list_by_filters` method but might need a specialized lightweight query for just the set data if performance becomes an issue. For now, reusing `list_by_filters` is acceptable.

```python
# Use existing method:
# await session_repository.list_by_filters(
#     exercise_id=exercise_id, 
#     status=SessionStatus.COMPLETED,
#     limit=1000  # Reasonable limit for history
# )
```

### Step 3: Implement Service Logic

**File**: `src/app/application/services/insight_service.py`

```python
from app.application.dto.insight import PersonalRecordDTO, ExercisePersonalRecordsDTO
from app.domain.entities.session import SessionStatus

async def get_exercise_personal_records(
    self, exercise_id: UUID
) -> ExercisePersonalRecordsDTO:
    async with self.uow:
        # 1. Fetch sessions
        sessions = await self.uow.session_repository.list_by_filters(
            exercise_id=exercise_id,
            status=SessionStatus.COMPLETED,
            limit=1000
        )
        
        # 2. Initialize trackers
        max_weight_pr = None
        max_volume_pr = None
        max_e1rm_pr = None
        reps_records = {}  # weight -> PersonalRecordDTO
        
        # 3. Iterate and calculate
        for session in sessions:
            # Find the specific exercise within the session
            # (Logic to extract specific session_exercise and its sets)
            # ... calculation logic ...
            pass
            
        # 4. Construct and return DTO
        return ExercisePersonalRecordsDTO(...)

async def get_recent_personal_records(
    self, limit: int = 10, date_from: date | None = None
) -> list[PersonalRecordDTO]:
    # This might require a more complex query or fetching all PRs and sorting
    # For Phase 2, fetching recent completed sessions and checking for PRs 
    # might be expensive. A simplified approach:
    # Fetch last N completed sessions, check if they were PRs at the time.
    # OR: Just implement per-exercise PRs first.
    pass
```

### Step 4: Add GraphQL Types

**File**: `src/app/presentation/graphql/types/insight.py`

```python
import strawberry
from typing import Optional, List
from uuid import UUID
from datetime import datetime

@strawberry.type
class PersonalRecord:
    exercise_id: UUID
    exercise_name: str
    record_type: str
    value: float
    recorded_at: datetime
    session_id: UUID
    # details as JSON scalar or specific type

@strawberry.type
class ExercisePersonalRecords:
    exercise_id: UUID
    exercise_name: str
    max_weight: Optional[PersonalRecord]
    max_volume_single_session: Optional[PersonalRecord]
    max_reps_at_weight: List[PersonalRecord]
    estimated_one_rep_max: Optional[PersonalRecord]
```

### Step 5: Add GraphQL Resolvers

**File**: `src/app/presentation/graphql/resolvers/insight.py`

```python
@strawberry.field
async def exercise_personal_records(
    self, info: Info, exercise_id: UUID
) -> ExercisePersonalRecords:
    return await info.context.insight_service.get_exercise_personal_records(exercise_id)
```

---

## Testing Strategy

### Unit Tests
- Create mock sessions with specific sets (e.g., Session A: 100kg x 5, Session B: 110kg x 3).
- Verify `max_weight` logic picks 110kg.
- Verify `estimated_1rm` logic calculates correct Epley values.
- Verify `max_volume` logic sums (reps * weight) correctly.

### Integration Tests
- Seed database with a history of sessions for "Bench Press".
- Call `get_exercise_personal_records`.
- Assert the returned DTO matches the expected bests from the seed data.

### API Tests
- Execute GraphQL query `exercisePersonalRecords`.
- Verify JSON structure and data types.

---

## Files to Modify

1. `src/app/application/dto/insight.py` (New DTOs)
2. `src/app/application/services/insight_service.py` (New methods)
3. `src/app/presentation/graphql/types/insight.py` (New GraphQL types)
4. `src/app/presentation/graphql/resolvers/insight.py` (New resolver)
5. `tests/unit/services/test_insight_service.py` (Tests)
6. `tests/integration/test_insight_api.py` (Tests)

---

## Success Criteria Checklist

- [ ] `ExercisePersonalRecordsDTO` populated correctly
- [ ] Max Weight calculation is accurate
- [ ] Max Volume calculation is accurate
- [ ] Estimated 1RM calculation is accurate (Epley formula)
- [ ] Max Reps logic groups by weight correctly
- [ ] Only COMPLETED sessions are considered
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] GraphQL query returns data

---

## Commands to Run

```bash
# Run unit tests
uv run pytest tests/unit/services/test_insight_service.py -v

# Run integration tests
uv run pytest tests/integration/test_insight_api.py -v

# Check types
uv run mypy src/app/application/services/insight_service.py
```

---

## Subagent Assignment

**Subagent Type**: `general`

**Task Description**:
```
Implement the Personal Records System (Task 05).

1. Define PersonalRecordDTO and ExercisePersonalRecordsDTO in `src/app/application/dto/insight.py`.
2. Implement `get_exercise_personal_records` in `InsightService`.
   - Use `session_repository.list_by_filters` to get completed sessions.
   - Iterate sessions -> session_exercises -> sets to find max weight, volume, 1RM.
   - Use `calculate_epley_1rm` from domain logic if available, else implement `weight * (1 + reps/30)`.
3. Create GraphQL types in `src/app/presentation/graphql/types/insight.py`.
4. Add `exercisePersonalRecords` query to `InsightQuery` class in `src/app/presentation/graphql/resolvers/insight.py`.
5. Write unit tests in `tests/unit/services/test_insight_service.py` verifying all calculation logic.
6. Write integration tests in `tests/integration/test_insight_api.py`.

Ensure code is fully typed and passes linting.
```

---

## Next Steps

After completion, verify tests pass and move to [Task 06: Exercise Trend Analysis](./06-exercise-trend-analysis.md).
