# Task 01: Fix Session Filtering

**Phase**: 1 - Foundation Fixes & Filtering  
**Estimated Time**: 1-2 days  
**Priority**: Critical  
**Status**: Ready for Implementation

---

## User Story

**As a** user  
**I want to** filter sessions by status, mesocycle, and date range  
**So that** I can easily find specific workout sessions

---

## Background

The session filtering parameters (`status`, `mesocycle_id`, `date_from`, `date_to`) are currently **defined in the GraphQL API** but are **not implemented** in the service layer. The service currently only passes pagination to the repository, ignoring all filter parameters.

**Current Issue** (line 78 in `session.py` resolver):
```python
# TODO: Filters not yet implemented in service
items = await service.list_sessions(pagination)
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] Sessions can be filtered by `status` (PLANNED, IN_PROGRESS, COMPLETED)
- [ ] Sessions can be filtered by `mesocycle_id` (UUID)
- [ ] Sessions can be filtered by `date_from` (inclusive)
- [ ] Sessions can be filtered by `date_to` (inclusive)
- [ ] Filters can be combined (e.g., completed sessions in a mesocycle within date range)
- [ ] Pagination works correctly with filters

### Technical Requirements
- [ ] Repository method `list_by_filters()` properly implements all filters
- [ ] Repository method `count_by_filters()` uses same filter logic
- [ ] Service passes all filter parameters to repository
- [ ] Date filters work with `started_at` timestamp field
- [ ] Filters are optional (None = no filter applied)

### Testing Requirements
- [ ] Unit tests for service filtering logic (≥85% coverage)
- [ ] Integration tests for repository filtering (all filter combinations)
- [ ] GraphQL API tests for end-to-end filtering
- [ ] Test edge cases (no results, all filters applied, etc.)

---

## Implementation Plan

### Step 1: Update Repository Layer

**File**: `src/app/infrastructure/database/repositories/session.py`

**Current State**: Method `list_by_filters()` exists but may not handle all filters correctly.

**Tasks**:
1. Review existing `list_by_filters()` implementation
2. Ensure `status` filter is implemented:
   ```python
   if status:
       filters.append(SessionTable.status == status)
   ```
3. Ensure `mesocycle_id` filter is implemented:
   ```python
   if mesocycle_id:
       filters.append(SessionTable.mesocycle_id == mesocycle_id)
   ```
4. Ensure date filters use `started_at` field:
   ```python
   if date_from:
       filters.append(cast(SessionTable.started_at, Date) >= date_from)
   if date_to:
       filters.append(cast(SessionTable.started_at, Date) <= date_to)
   ```
5. Verify `count_by_filters()` uses the exact same filter logic
6. Ensure proper relationship loading with `selectinload()`

**Expected Signature**:
```python
async def list_by_filters(
    self,
    status: SessionStatus | None = None,
    mesocycle_id: UUID | None = None,
    exercise_id: UUID | None = None,  # existing
    date_from: date | None = None,
    date_to: date | None = None,
    offset: int = 0,
    limit: int = 20,
) -> Sequence[Session]:
    # Implementation
```

---

### Step 2: Update Service Layer

**File**: `src/app/application/services/session_service.py`

**Current State**: `list_sessions()` only accepts `pagination` parameter.

**Tasks**:
1. Update method signature to accept filter parameters:
   ```python
   async def list_sessions(
       self,
       pagination: PaginationInput,
       status: SessionStatus | None = None,
       mesocycle_id: UUID | None = None,
       date_from: date | None = None,
       date_to: date | None = None,
   ) -> PaginatedSessions:
   ```

2. Pass all filters to repository:
   ```python
   async with self.uow:
       offset = (pagination.page - 1) * pagination.page_size
       limit = pagination.page_size
       
       items = await self.uow.session_repository.list_by_filters(
           status=status,
           mesocycle_id=mesocycle_id,
           date_from=date_from,
           date_to=date_to,
           offset=offset,
           limit=limit,
       )
       
       total = await self.uow.session_repository.count_by_filters(
           status=status,
           mesocycle_id=mesocycle_id,
           date_from=date_from,
           date_to=date_to,
       )
       
       # Calculate and return paginated result
   ```

---

### Step 3: Update GraphQL Resolver

**File**: `src/app/presentation/graphql/resolvers/session.py`

**Current State**: Resolver receives filter parameters but doesn't pass them to service.

**Tasks**:
1. Remove the TODO comment on line 78
2. Pass all filter parameters to service:
   ```python
   @strawberry.field
   async def sessions(
       self,
       info: Info,
       pagination: PaginationInput | None = None,
       status: SessionStatus | None = None,
       mesocycle_id: UUID | None = None,
       date_from: date | None = None,
       date_to: date | None = None,
   ) -> PaginatedSessions:
       service = info.context.session_service
       pagination = pagination or PaginationInput()
       
       result = await service.list_sessions(
           pagination=pagination,
           status=status,
           mesocycle_id=mesocycle_id,
           date_from=date_from,
           date_to=date_to,
       )
       
       return result
   ```

---

### Step 4: Write Unit Tests

**File**: `tests/unit/services/test_session_service.py`

**Tasks**:
1. Test filtering by status:
   ```python
   @pytest.mark.asyncio
   async def test_list_sessions_filter_by_status(service, mock_uow):
       # Arrange
       pagination = PaginationInput(page=1, page_size=10)
       mock_uow.session_repository.list_by_filters = AsyncMock(return_value=[])
       mock_uow.session_repository.count_by_filters = AsyncMock(return_value=0)
       
       # Act
       await service.list_sessions(
           pagination, 
           status=SessionStatus.COMPLETED
       )
       
       # Assert
       mock_uow.session_repository.list_by_filters.assert_called_once_with(
           status=SessionStatus.COMPLETED,
           mesocycle_id=None,
           date_from=None,
           date_to=None,
           offset=0,
           limit=10,
       )
   ```

2. Test filtering by mesocycle_id
3. Test filtering by date range
4. Test combining multiple filters
5. Test with no filters (should work as before)

---

### Step 5: Write Integration Tests

**File**: `tests/integration/test_session_repository.py`

**Tasks**:
1. Create test sessions with different statuses, mesocycles, and dates
2. Test status filtering:
   ```python
   @pytest.mark.asyncio
   async def test_session_repository_filter_by_status(db_session: AsyncSession):
       repo = SQLAlchemySessionRepository(db_session)
       
       # Create sessions with different statuses
       completed = Session(id=uuid4(), status=SessionStatus.COMPLETED, ...)
       planned = Session(id=uuid4(), status=SessionStatus.PLANNED, ...)
       await repo.add(completed)
       await repo.add(planned)
       
       # Filter by completed
       results = await repo.list_by_filters(status=SessionStatus.COMPLETED)
       
       # Assert
       assert len(results) == 1
       assert results[0].status == SessionStatus.COMPLETED
   ```

3. Test mesocycle filtering
4. Test date range filtering
5. Test combination of filters
6. Test count_by_filters matches list_by_filters

---

### Step 6: Write GraphQL API Tests

**File**: `tests/integration/test_session_api.py`

**Tasks**:
1. Test GraphQL query with status filter:
   ```python
   @pytest.mark.anyio
   async def test_sessions_filter_by_status(client: AsyncClient, auth_headers: dict):
       # Setup: Create sessions with different statuses
       # ...
       
       # Query with filter
       query = """
       query GetSessions($status: SessionStatus) {
           sessions(status: $status) {
               items { id status }
               total
           }
       }
       """
       
       response = await client.post(
           "/graphql",
           json={"query": query, "variables": {"status": "COMPLETED"}},
           headers=auth_headers,
       )
       
       # Assert
       assert response.status_code == 200
       data = response.json()["data"]["sessions"]
       assert all(s["status"] == "COMPLETED" for s in data["items"])
   ```

2. Test date range filtering via GraphQL
3. Test mesocycle filtering via GraphQL
4. Test multiple filters combined
5. Test pagination works with filters

---

## Testing Strategy

### Unit Tests (Mock-based)
- **Focus**: Service layer business logic
- **Coverage Target**: 100% of filtering logic
- **Verify**: Correct parameters passed to repository

### Integration Tests (Database)
- **Focus**: Repository SQL queries
- **Coverage Target**: All filter combinations
- **Verify**: Correct data returned from database

### API Tests (GraphQL)
- **Focus**: End-to-end functionality
- **Coverage Target**: All user-facing scenarios
- **Verify**: Filters work through complete request cycle

---

## Files to Modify

1. `src/app/infrastructure/database/repositories/session.py` - Update `list_by_filters()` and `count_by_filters()`
2. `src/app/application/services/session_service.py` - Update `list_sessions()` signature and implementation
3. `src/app/presentation/graphql/resolvers/session.py` - Pass filters to service
4. `tests/unit/services/test_session_service.py` - Add filter tests
5. `tests/integration/test_session_repository.py` - Add repository filter tests
6. `tests/integration/test_session_api.py` - Add GraphQL filter tests

---

## Success Criteria Checklist

- [ ] Repository filters implemented and working
- [ ] Service passes all filters to repository
- [ ] GraphQL resolver passes all filters to service
- [ ] All unit tests pass (≥85% coverage on new code)
- [ ] All integration tests pass
- [ ] All GraphQL API tests pass
- [ ] Existing tests still pass (no regressions)
- [ ] Code follows existing patterns
- [ ] No linting errors

---

## Commands to Run

```bash
# Run all tests
uv run pytest

# Run session-specific tests
uv run pytest tests/unit/services/test_session_service.py -v
uv run pytest tests/integration/test_session_repository.py -v
uv run pytest tests/integration/test_session_api.py -v

# Run with coverage
uv run pytest --cov=app.application.services.session_service --cov=app.infrastructure.database.repositories.session --cov-report=term-missing

# Lint check
uv run ruff check src/app/application/services/session_service.py
uv run ruff check src/app/infrastructure/database/repositories/session.py
```

---

## Implementation Notes

### Date Handling
- Use `cast(SessionTable.started_at, Date)` to extract date from timestamp
- Date filters are inclusive (≥ date_from, ≤ date_to)
- Handle None gracefully (no filter applied)

### Filter Combination
- All filters use AND logic (all must match)
- Use SQLAlchemy's `and_(*filters)` for combining

### Performance
- Ensure indexes exist on filtered columns (started_at, status, mesocycle_id)
- Use `unique()` when joining to avoid duplicate results

---

## Subagent Assignment

**Subagent Type**: `general`

**Task Description**:
```
Implement session filtering for the Workout Tracker API. The filtering parameters (status, mesocycle_id, date_from, date_to) are defined in the GraphQL API but not implemented in the service/repository layers.

1. Update SessionRepository.list_by_filters() to properly implement all filters
2. Update SessionRepository.count_by_filters() with same logic
3. Update SessionService.list_sessions() to accept and pass filter parameters
4. Update GraphQL resolver to pass filters to service
5. Write comprehensive unit tests for service filtering
6. Write integration tests for repository filtering
7. Write GraphQL API tests for end-to-end filtering

Follow the existing code patterns in the codebase. Ensure all tests pass and coverage is ≥85% on new code.

Return confirmation when complete with test results.
```

---

## Next Steps

After completing this task:
1. Run full test suite to ensure no regressions
2. Commit changes: `git commit -m "feat: implement session filtering (status, mesocycle, dates)"`
3. Move to [Task 02: Fix Bodyweight Filtering](./02-fix-bodyweight-filtering.md)

---

**Ready to implement?** Assign this task to a subagent or begin implementation following the plan above.
