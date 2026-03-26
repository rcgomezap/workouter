# Task 04: Phase 1 Integration Testing

**Status**: Not Started  
**Priority**: High  
**Estimated Time**: 1 day  
**Dependencies**: Tasks 01, 02, 03  
**Phase**: 1 - Foundation & Stability

## Overview

Comprehensive integration testing to validate all Phase 1 changes work together correctly. This task ensures the GraphQL schema changes, new features, and bug fixes integrate seamlessly without regressions.

## Scope

### 1. Schema Consistency Tests
Validate the exported GraphQL schema matches the implementation:

```python
async def test_schema_export_matches_runtime():
    """Ensure exported schema.graphql is up-to-date"""
    # Compare exported schema with runtime schema
    # Fail if they differ (indicates schema.graphql needs regeneration)
```

### 2. Exercise History Integration Tests
Test the complete flow from creation to history retrieval:

```python
async def test_exercise_history_full_flow():
    """Test exercise history across multiple routines and sessions"""
    # Create mesocycle with 2 routines
    # Each routine has 2 sessions with the same exercise
    # Log sets for each session
    # Query exerciseHistory with and without routine_id filter
    # Verify correct filtering and aggregation
```

### 3. Bodyweight Tracking Integration Tests
Test the interaction between bodyweight logs and sessions:

```python
async def test_bodyweight_session_integration():
    """Test bodyweight logs are correctly associated with sessions"""
    # Create session with bodyweight log
    # Query session and verify bodyweight is included
    # Query bodyweight history and verify session association
    
async def test_bodyweight_interpolation():
    """Test bodyweight interpolation for sessions without explicit logs"""
    # Create multiple sessions across time
    # Log bodyweight for some sessions
    # Verify interpolation fills gaps correctly
```

### 4. Progressive Overload Tests
Test progressive overload calculations across the new schema:

```python
async def test_progressive_overload_trends():
    """Test progressive overload metrics with bodyweight changes"""
    # Create progression over multiple weeks
    # Include bodyweight changes
    # Verify progressive overload calculations account for bodyweight
```

### 5. Cascade Deletion Tests
Verify proper cascading when deleting entities:

```python
async def test_delete_routine_cascades():
    """Test deleting a routine properly cascades to sessions and logs"""
    # Create routine with sessions, sets, and logs
    # Delete routine
    # Verify all related data is properly handled
```

### 6. Concurrent Operation Tests
Test for race conditions and concurrent updates:

```python
async def test_concurrent_set_logging():
    """Test multiple users logging sets simultaneously"""
    # Simulate concurrent set log creation
    # Verify data integrity and no duplicates
```

## Test Organization

Create new integration test file:
- `tests/integration/test_phase1_integration.py`

Update existing integration tests if needed:
- `tests/integration/test_graphql_queries.py`
- `tests/integration/test_set_log_queries.py`

## Acceptance Criteria

- [ ] All new integration tests pass
- [ ] All existing integration tests still pass
- [ ] Test coverage for new features is ≥ 90%
- [ ] Schema export test validates consistency
- [ ] Cascade deletion test validates data integrity
- [ ] Concurrent operation test validates thread safety
- [ ] Performance benchmarks show no regression (queries < 500ms)

## Testing Checklist

- [ ] Run full test suite: `uv run pytest`
- [ ] Run with coverage: `uv run pytest --cov=app --cov-report=html`
- [ ] Review coverage report for gaps
- [ ] Test with production-like data volume (100+ sessions)
- [ ] Manually test GraphQL queries in playground
- [ ] Verify schema.graphql is up-to-date

## Performance Benchmarks

Expected query performance (with 1000 set logs):
- `exerciseHistory`: < 200ms
- `workoutSession` with nested data: < 100ms
- `bodyweightHistory`: < 50ms

Run benchmarks with:
```bash
uv run pytest tests/integration/test_performance.py --benchmark
```

## Related Files

- `tests/integration/test_phase1_integration.py` - New integration tests
- `tests/conftest.py` - Shared fixtures
- `src/export_schema.py` - Schema export script
- `schema.graphql` - Exported schema

## Regression Prevention

Key areas to verify for regressions:
1. **Existing GraphQL Queries**: All existing queries still work
2. **Data Integrity**: No orphaned records after operations
3. **Performance**: No N+1 query issues introduced
4. **Authentication**: API key validation still enforces correctly
5. **Error Handling**: Proper error messages for invalid inputs

## Documentation Updates

After tests pass:
- [ ] Update `README.md` with any new testing instructions
- [ ] Document any new test fixtures or utilities
- [ ] Add examples of new GraphQL queries to docs
- [ ] Update API documentation with schema changes

## Success Metrics

- All Phase 1 tasks (01, 02, 03) are validated through integration tests
- Zero regressions in existing functionality
- Test suite completes in < 30 seconds
- 100% of critical paths have integration test coverage

## Notes

- This task acts as the **quality gate** for Phase 1
- Do not proceed to Phase 2 until all tests pass
- If integration issues are found, create new bug fix tasks
- Consider this the "Phase 1 sign-off" task

## Next Steps After Completion

- Generate final test coverage report
- Review Phase 1 completion with stakeholders
- Begin Phase 2 planning (see `docs/enhancement/phase2-analytics.md`)
- Tag a release: `v1.1.0-phase1`
