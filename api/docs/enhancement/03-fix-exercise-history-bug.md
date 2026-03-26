# Task 03: Fix Exercise History Bug

**Status**: Completed
**Priority**: High
**Estimated Time**: 1-2 days
**Dependencies**: None
**Phase**: 1 - Foundation & Stability

## Problem Statement

The `exerciseHistory` query previously returned incorrect data when filtering by `routine_id`. The issue was that the query fetched all sessions for an exercise without applying the `routine_id` filter to the sessions themselves.

**Example of incorrect behavior**:
```graphql
query {
  exerciseHistory(exerciseId: 1, routineId: 2) {
    sets {
      # Returns sets from ALL routines, not just routine 2
    }
  }
}
```

## Root Cause

The `SessionRepository.list_by_filters` method did not support filtering by `routine_id`. Consequently, the `InsightService.get_exercise_history` method could not restrict the history to a specific routine.

## Solution

### Implemented Fix

Instead of the originally proposed schema migration (adding `session_id` to `WorkoutSet`), we utilized the existing data model where `Session` already contains `routine_id`.

1.  **Repository Update**: Updated `SQLAlchemySessionRepository.list_by_filters` in `src/app/infrastructure/database/repositories/session.py` to accept `routine_id` as a filter argument.
2.  **Domain Interface Update**: Updated `SessionRepository` protocol in `src/app/domain/repositories/session.py` to match the implementation.
3.  **Service Update**: Updated `InsightService.get_exercise_history` in `src/app/application/services/insight_service.py` to accept `routine_id` and pass it to the repository.
4.  **GraphQL Resolver Update**: Updated `InsightQuery.exercise_history` in `src/app/presentation/graphql/resolvers/insight.py` to accept `routineId` as an optional argument.

### Logic

```python
# src/app/infrastructure/database/repositories/session.py

stmt = select(SessionTable)
if routine_id:
    stmt = stmt.where(SessionTable.routine_id == routine_id)
# ... other filters
```

## Verification

### Integration Test
Created `tests/integration/test_exercise_history_bug.py` (renamed/merged into `tests/integration/test_insight_history.py`) to verify the fix.

**Test Scenario**:
1.  Create two routines (Routine A, Routine B).
2.  Create sessions for both routines containing the same exercise.
3.  Query `exerciseHistory` with `routineId` for Routine A.
4.  Assert that only the session from Routine A is returned.

**Result**: PASS

### Regression Testing
Ran full test suite (`uv run pytest`). All tests passed.

## Acceptance Criteria Status

- [x] `exerciseHistory` query correctly filters by `routine_id`
- [x] Integration test verifies filtering behavior
- [x] All existing tests still pass
- [x] No breaking changes to GraphQL schema (routineId is optional)

## Related Files

- `src/app/infrastructure/database/repositories/session.py`
- `src/app/domain/repositories/session.py`
- `src/app/application/services/insight_service.py`
- `src/app/presentation/graphql/resolvers/insight.py`
- `tests/integration/test_insight_history.py`
