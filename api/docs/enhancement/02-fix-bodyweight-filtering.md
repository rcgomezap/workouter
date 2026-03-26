# Task 02: Fix Bodyweight Date Filtering

**Phase**: 1 - Foundation Fixes & Filtering  
**Estimated Time**: 0.5-1 day  
**Priority**: High  
**Status**: Ready for Implementation

---

## User Story

**As a** user  
**I want to** filter bodyweight logs by date range  
**So that** I can view my weight trends for specific time periods

---

## Background

The bodyweight filtering parameters (`date_from`, `date_to`) are currently **defined in the GraphQL API** but are **not implemented** in the service layer. The repository layer already has the `list_by_date_range()` and `count_by_date_range()` methods fully implemented, but the service ignores these filter parameters and always calls the generic `list()` method instead.

**Current Issue** (line 29 in `bodyweight_service.py`):
```python
# Service only uses list() - date filters ignored
logs = await self.uow.bodyweight_repository.list(offset=offset, limit=limit)
total = await self.uow.bodyweight_repository.count()
```

**GraphQL Resolver Issue** (line 35 in `bodyweight.py` resolver):
```python
# Resolver receives date_from/date_to but doesn't pass them to service
result = await info.context.bodyweight_service.list_bodyweight_logs(p_dto)
```

**Good News**: The repository layer (`src/app/infrastructure/database/repositories/bodyweight.py`) already has complete filtering implementation with `list_by_date_range()` and `count_by_date_range()` methods!

---

## Acceptance Criteria

### Functional Requirements
- [ ] Bodyweight logs can be filtered by `date_from` (inclusive)
- [ ] Bodyweight logs can be filtered by `date_to` (inclusive)
- [ ] Date range filters work with `recorded_at` timestamp field
- [ ] Filters are optional (None = no filter applied)
- [ ] Pagination works correctly with date filters

### Technical Requirements
- [ ] Service passes date filter parameters to repository
- [ ] Service calls `list_by_date_range()` instead of `list()`
- [ ] Service calls `count_by_date_range()` instead of `count()`
- [ ] Repository methods are reused (no changes needed to repository)

### Testing Requirements
- [ ] Unit tests for service filtering logic (≥85% coverage)
- [ ] Integration tests for end-to-end filtering
- [ ] GraphQL API tests for date range filtering
- [ ] Test edge cases (no results, single date, wide range)

---

## Implementation Plan

### Step 1: Update Service Layer

**File**: `src/app/application/services/bodyweight_service.py`

**Current State**: Line 25-37 only accepts `pagination` parameter and ignores date filters.

**Tasks**:
1. Update method signature to accept date parameters:
   ```python
   async def list_bodyweight_logs(
       self,
       pagination: PaginationInput,
       date_from: date | None = None,
       date_to: date | None = None,
   ) -> PaginatedBodyweightLogs:
   ```

2. Replace `list()` and `count()` calls with date-aware methods:
   ```python
   async def list_bodyweight_logs(
       self,
       pagination: PaginationInput,
       date_from: date | None = None,
       date_to: date | None = None,
   ) -> PaginatedBodyweightLogs:
       async with self.uow:
           offset = (pagination.page - 1) * pagination.page_size
           limit = pagination.page_size
           
           # Use date-aware repository methods
           logs = await self.uow.bodyweight_repository.list_by_date_range(
               date_from=date_from,
               date_to=date_to,
               offset=offset,
               limit=limit,
           )
           
           total = await self.uow.bodyweight_repository.count_by_date_range(
               date_from=date_from,
               date_to=date_to,
           )
           
           return PaginatedBodyweightLogs(
               items=[self._map_to_dto(l) for l in logs],
               total=total,
               page=pagination.page,
               page_size=pagination.page_size,
               total_pages=(total + pagination.page_size - 1) // pagination.page_size,
           )
   ```

3. Add import for `date` type at top of file:
   ```python
   from datetime import date
   ```

---

### Step 2: Update GraphQL Resolver

**File**: `src/app/presentation/graphql/resolvers/bodyweight.py`

**Current State**: Line 24-42 receives date parameters but doesn't pass them to service.

**Tasks**:
1. Convert `datetime` parameters to `date` (GraphQL uses datetime, service uses date):
   ```python
   @strawberry.field
   async def bodyweight_logs(
       self,
       info: Info[Context, None],
       pagination: PaginationInput | None = None,
       date_from: datetime | None = None,
       date_to: datetime | None = None,
   ) -> PaginatedBodyweightLogs:
       p_dto = PaginationDTO(
           page=pagination.page if pagination else 1,
           page_size=pagination.page_size if pagination else 20,
       )
       
       # Convert datetime to date for service layer
       date_from_filter = date_from.date() if date_from else None
       date_to_filter = date_to.date() if date_to else None
       
       result = await info.context.bodyweight_service.list_bodyweight_logs(
           pagination=p_dto,
           date_from=date_from_filter,
           date_to=date_to_filter,
       )
       
       return PaginatedBodyweightLogs(
           items=[map_bodyweight_log(l) for l in result.items],
           total=result.total,
           page=result.page,
           page_size=result.page_size,
           total_pages=result.total_pages,
       )
   ```

---

### Step 3: Write Unit Tests

**File**: `tests/unit/services/test_bodyweight_service.py`

**Tasks**:
1. Test filtering by date_from:
   ```python
   @pytest.mark.asyncio
   async def test_list_bodyweight_logs_filter_by_date_from(service, mock_uow):
       # Arrange
       pagination = PaginationInput(page=1, page_size=10)
       target_date = date(2026, 1, 1)
       mock_uow.bodyweight_repository.list_by_date_range = AsyncMock(return_value=[])
       mock_uow.bodyweight_repository.count_by_date_range = AsyncMock(return_value=0)
       
       # Act
       await service.list_bodyweight_logs(
           pagination=pagination,
           date_from=target_date,
           date_to=None,
       )
       
       # Assert
       mock_uow.bodyweight_repository.list_by_date_range.assert_called_once_with(
           date_from=target_date,
           date_to=None,
           offset=0,
           limit=10,
       )
       mock_uow.bodyweight_repository.count_by_date_range.assert_called_once_with(
           date_from=target_date,
           date_to=None,
       )
   ```

2. Test filtering by date_to
3. Test filtering by date range (both date_from and date_to)
4. Test with no filters (should still work as before)
5. Test pagination offset calculation with filters

---

### Step 4: Write Integration Tests

**File**: `tests/integration/test_bodyweight_api.py`

**Tasks**:
1. Test GraphQL query with date_from filter:
   ```python
   @pytest.mark.asyncio
   async def test_bodyweight_logs_filter_by_date_from(client: AsyncClient, auth_headers: dict):
       # Setup: Create bodyweight logs on different dates
       # Log 1: 2026-01-01
       # Log 2: 2026-01-15
       # Log 3: 2026-02-01
       
       # Query with date_from filter
       query = """
       query GetBodyweightLogs($dateFrom: DateTime) {
           bodyweightLogs(dateFrom: $dateFrom) {
               items {
                   id
                   weightKg
                   recordedAt
               }
               total
           }
       }
       """
       
       response = await client.post(
           "/graphql",
           json={
               "query": query,
               "variables": {"dateFrom": "2026-01-15T00:00:00Z"}
           },
           headers=auth_headers,
       )
       
       # Assert - should only get logs from Jan 15 onwards
       assert response.status_code == 200
       data = response.json()["data"]["bodyweightLogs"]
       assert data["total"] == 2  # Only logs 2 and 3
       assert all(
           log["recordedAt"] >= "2026-01-15"
           for log in data["items"]
       )
   ```

2. Test date_to filter
3. Test date range filter (both date_from and date_to)
4. Test pagination with filters
5. Test edge cases (no logs in range, single date, wide range)

---

## Testing Strategy

### Unit Tests (Mock-based)
- **Focus**: Service layer parameter passing
- **Coverage Target**: 100% of filtering logic
- **Verify**: Correct parameters passed to repository methods
- **Verify**: Service uses `list_by_date_range()` not `list()`

### Integration Tests (Database)
- **Focus**: End-to-end filtering through GraphQL API
- **Coverage Target**: All date filter combinations
- **Verify**: Correct data returned from database
- **Verify**: datetime → date conversion works correctly

### API Tests (GraphQL)
- **Focus**: User-facing scenarios
- **Coverage Target**: Common use cases
- **Verify**: Filters work through complete request cycle
- **Verify**: Pagination metadata is correct with filters

---

## Files to Modify

1. `src/app/application/services/bodyweight_service.py` - Update `list_bodyweight_logs()` signature and implementation
2. `src/app/presentation/graphql/resolvers/bodyweight.py` - Pass date filters to service
3. `tests/unit/services/test_bodyweight_service.py` - Add date filter tests
4. `tests/integration/test_bodyweight_api.py` - Add GraphQL date filter tests

**Note**: Repository layer (`src/app/infrastructure/database/repositories/bodyweight.py`) requires NO changes - it already has complete filtering implementation!

---

## Success Criteria Checklist

- [ ] Service accepts date_from and date_to parameters
- [ ] Service calls `list_by_date_range()` instead of `list()`
- [ ] Service calls `count_by_date_range()` instead of `count()`
- [ ] GraphQL resolver passes date filters to service
- [ ] datetime → date conversion is correct in resolver
- [ ] All unit tests pass (≥85% coverage on new code)
- [ ] All integration tests pass
- [ ] Existing tests still pass (no regressions)
- [ ] Code follows existing patterns
- [ ] No linting errors

---

## Commands to Run

```bash
# Run all tests
uv run pytest

# Run bodyweight-specific tests
uv run pytest tests/unit/services/test_bodyweight_service.py -v
uv run pytest tests/integration/test_bodyweight_api.py -v

# Run with coverage
uv run pytest --cov=app.application.services.bodyweight_service --cov-report=term-missing

# Lint check
uv run ruff check src/app/application/services/bodyweight_service.py
uv run ruff check src/app/presentation/graphql/resolvers/bodyweight.py

# Type check
uv run mypy src/app/application/services/bodyweight_service.py
```

---

## Implementation Notes

### Date vs Datetime Handling
- **GraphQL Layer**: Uses `datetime` (ISO 8601 format)
- **Service Layer**: Uses `date` (date only)
- **Repository Layer**: Uses `func.date()` to extract date from `recorded_at` timestamp
- **Conversion**: Resolver must call `.date()` on datetime objects before passing to service

### Filter Inclusivity
- Both `date_from` and `date_to` are inclusive
- `date_from`: `recorded_at >= date_from` (logs on or after date)
- `date_to`: `recorded_at <= date_to` (logs on or before date)

### Repository Methods Already Exist
The repository already has these methods implemented correctly:
- `list_by_date_range(date_from, date_to, offset, limit)`
- `count_by_date_range(date_from, date_to)`

This task is primarily about **wiring** - connecting the GraphQL API → Service → Repository layers.

---

## Subagent Assignment

**Subagent Type**: `general`

**Task Description**:
```
Implement bodyweight date filtering for the Workout Tracker API. The date filter parameters (date_from, date_to) are defined in the GraphQL API but not passed through to the service layer. The repository layer already has full filtering implementation.

1. Update BodyweightService.list_bodyweight_logs() to accept date_from and date_to parameters
2. Update service to call list_by_date_range() instead of list()
3. Update service to call count_by_date_range() instead of count()
4. Update GraphQL resolver to pass date filters to service (convert datetime → date)
5. Write unit tests for service date filtering
6. Write integration tests for GraphQL date filtering

Follow the existing code patterns in the codebase. Ensure all tests pass and coverage is ≥85% on new code.

Return confirmation when complete with test results.
```

---

## Next Steps

After completing this task:
1. Run full test suite to ensure no regressions
2. Test manually with GraphQL playground:
   ```graphql
   query {
     bodyweightLogs(
       dateFrom: "2026-01-01T00:00:00Z"
       dateTo: "2026-03-31T23:59:59Z"
     ) {
       items { id weightKg recordedAt }
       total
     }
   }
   ```
3. Commit changes: `git commit -m "feat: implement bodyweight date filtering"`
4. Move to [Task 03: Fix Exercise History Bug](./03-fix-exercise-history-bug.md)

---

**Ready to implement?** Assign this task to a subagent or begin implementation following the plan above.
