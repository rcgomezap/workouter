# Task 03: Fix Exercise History Bug

**Status**: Not Started  
**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: None  
**Phase**: 1 - Foundation & Stability

## Problem Statement

The `exerciseHistory` query currently returns incorrect data when filtering by `routine_id`. Analysis shows:
1. The query filters `WorkoutSession` by `routine_id`, but then joins to `SetLog` via `WorkoutSet`
2. `WorkoutSet` has no direct relationship to `WorkoutSession.routine_id`
3. This causes the query to return ALL exercise history instead of filtering by routine

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

In `src/app/infrastructure/repositories/set_log_repository.py:76-90`:

```python
query = select(SetLog).join(WorkoutSet).join(Exercise)

if routine_id:
    query = query.join(WorkoutSession).where(WorkoutSession.routine_id == routine_id)
```

**Issue**: The join chain is broken because:
- `WorkoutSet` does NOT have a `session_id` or direct relationship to `WorkoutSession`
- The intended data model should link: `SetLog → WorkoutSet → WorkoutSession → Routine`
- Currently missing: the FK from `WorkoutSet` to `WorkoutSession`

## Solution

### Step 1: Add Missing Foreign Key
Add `session_id` column to `workout_set` table:

```sql
-- New migration
ALTER TABLE workout_set ADD COLUMN session_id INTEGER;
ALTER TABLE workout_set ADD CONSTRAINT fk_workout_set_session 
  FOREIGN KEY (session_id) REFERENCES workout_session(id);
```

Update `WorkoutSet` model in `src/app/infrastructure/database/models.py`:

```python
class WorkoutSet(Base):
    __tablename__ = "workout_set"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id"))
    session_id: Mapped[int] = mapped_column(ForeignKey("workout_session.id"))  # ADD THIS
    set_number: Mapped[int]
    target_reps: Mapped[int | None]
    target_weight: Mapped[float | None]
    target_duration: Mapped[int | None]
    
    # Relationships
    exercise: Mapped["Exercise"] = relationship(back_populates="workout_sets")
    session: Mapped["WorkoutSession"] = relationship(back_populates="workout_sets")  # ADD THIS
    set_logs: Mapped[list["SetLog"]] = relationship(back_populates="workout_set")
```

### Step 2: Fix Repository Query
Update `SetLogRepository.get_by_exercise()` to use the new FK:

```python
query = select(SetLog).join(WorkoutSet).join(Exercise)

if routine_id:
    query = query.join(WorkoutSession, WorkoutSet.session_id == WorkoutSession.id)\
                 .where(WorkoutSession.routine_id == routine_id)
```

### Step 3: Update Service Layer
Review `SetLogService.get_exercise_history()` to ensure it properly handles the filtered data.

### Step 4: Add Integration Test
Create test in `tests/integration/test_exercise_history.py`:

```python
async def test_exercise_history_filters_by_routine():
    """Verify exerciseHistory only returns data for the specified routine"""
    # Setup: Create 2 routines, each with sessions containing the same exercise
    # Query: exerciseHistory(exerciseId=X, routineId=1)
    # Assert: Only sets from routine 1 are returned
```

## Acceptance Criteria

- [ ] `workout_set` table has `session_id` FK to `workout_session`
- [ ] All existing `WorkoutSet` records are migrated with correct `session_id`
- [ ] `exerciseHistory` query correctly filters by `routine_id`
- [ ] Integration test verifies filtering behavior
- [ ] All existing tests still pass
- [ ] No breaking changes to GraphQL schema

## Testing Strategy

1. **Unit Tests**: Test repository filtering logic
2. **Integration Tests**: Test end-to-end GraphQL query with multiple routines
3. **Migration Test**: Verify existing data is correctly migrated

## Implementation Checklist

- [ ] Create Alembic migration for `workout_set.session_id`
- [ ] Update `WorkoutSet` SQLAlchemy model
- [ ] Update `WorkoutSession` model to include `workout_sets` relationship
- [ ] Fix `SetLogRepository.get_by_exercise()` query logic
- [ ] Add integration test for routine filtering
- [ ] Run full test suite
- [ ] Manually test with GraphQL playground
- [ ] Update any affected documentation

## Related Files

- `src/app/infrastructure/database/models.py` - WorkoutSet and WorkoutSession models
- `src/app/infrastructure/repositories/set_log_repository.py` - Query logic
- `src/app/application/services/set_log_service.py` - Business logic
- `src/app/presentation/graphql/resolvers/queries.py` - GraphQL resolver
- `alembic/versions/` - New migration file

## Notes

- This is a **critical bug** that affects data accuracy for users with multiple routines
- The fix requires a schema migration, so coordinate with any production deployments
- Consider if any other queries might be affected by the missing FK
- After this fix, consider adding a database constraint to prevent orphaned `WorkoutSet` records

## Next Steps After Completion

- Verify no other queries have similar join issues
- Consider adding relationship validation in the domain layer
- Update API documentation to clarify the routine filtering behavior
