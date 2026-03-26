# Workout Tracker API Enhancement Plan

## Overview

This document outlines a comprehensive enhancement plan to transform the Workout Tracker API from a single-user workout tracker into a robust personal training platform with advanced analytics, search, and tracking capabilities.

## Timeline & Phases

**Total Duration**: 7 weeks (49 days)

| Phase | Duration | Focus Area | Tasks |
|-------|----------|------------|-------|
| Phase 1 | 5-7 days | Foundation Fixes & Filtering | 01-04 |
| Phase 2 | 10-12 days | Enhanced Analytics Core | 05-08 |
| Phase 3 | 10-12 days | Advanced Insights & Benchmarking | 09-13 |
| Phase 4 | 8-10 days | Search, Discovery & Session Lifecycle | 14-18 |
| Phase 5 | 8-10 days | Bodyweight & Composition Analytics | 19-23 |
| Phase 6 | 8-10 days | Feedback & Final Polish | 24-28 |

## Implementation Strategy

### Subagent Usage

- **`general` subagent**: Feature implementation, testing, bug fixing
- **`explore` subagent**: Performance analysis, code exploration, optimization

### Development Pattern

Each task follows this pattern:
1. **Planning** (Main agent): Define scope, interfaces, files
2. **Implementation** (Subagent): Write code, tests
3. **Review** (Main agent): Verify, run tests
4. **Integration** (Subagent/Main): Ensure no regressions

### Testing Requirements

Every task includes:
- ✅ Unit tests (service layer)
- ✅ Integration tests (repository + API)
- ✅ GraphQL end-to-end tests
- ✅ Coverage ≥85% for new code

## Phase Details

### Phase 1: Foundation Fixes & Filtering 🔧

**Goal**: Fix broken features and establish filtering infrastructure

**Tasks**:
- [01-fix-session-filtering.md](./01-fix-session-filtering.md) - Implement session filter parameters
- [02-fix-bodyweight-filtering.md](./02-fix-bodyweight-filtering.md) - Implement bodyweight date filters
- [03-fix-exercise-history-bug.md](./03-fix-exercise-history-bug.md) - Fix empty exercise arrays bug
- [04-phase1-integration-testing.md](./04-phase1-integration-testing.md) - Comprehensive Phase 1 validation

**Success Criteria**:
- [ ] Session filtering works (status, mesocycle_id, date_from, date_to)
- [ ] Bodyweight date filtering works
- [ ] Exercise history returns full data
- [ ] All existing tests pass
- [ ] No regressions

---

### Phase 2: Enhanced Analytics Core 📊

**Goal**: Build robust analytics for PRs, trends, and progression

**Tasks**:
- [05-personal-records-system.md](./05-personal-records-system.md) - Track all-time PRs
- [06-exercise-trend-analysis.md](./06-exercise-trend-analysis.md) - Identify improvement/plateau/regression
- [07-exercise-volume-progression.md](./07-exercise-volume-progression.md) - Volume over time tracking
- [08-phase2-integration-testing.md](./08-phase2-integration-testing.md) - Comprehensive Phase 2 validation

**Success Criteria**:
- [ ] Can query PRs for any exercise (max weight, volume, reps, 1RM)
- [ ] Trend analysis identifies patterns correctly
- [ ] Volume progression data accurate
- [ ] All calculations verified manually
- [ ] Tests achieve >85% coverage

---

### Phase 3: Advanced Insights & Benchmarking 🎯

**Goal**: Add muscle analysis, intensity tracking, and comparisons

**Tasks**:
- [09-muscle-group-imbalance.md](./09-muscle-group-imbalance.md) - Detect volume disparities
- [10-intensity-distribution.md](./10-intensity-distribution.md) - RIR distribution analysis
- [11-mesocycle-adherence.md](./11-mesocycle-adherence.md) - Track completion rates
- [12-comparison-benchmarking.md](./12-comparison-benchmarking.md) - Compare exercises and mesocycles
- [13-phase3-integration-testing.md](./13-phase3-integration-testing.md) - Comprehensive Phase 3 validation

**Success Criteria**:
- [ ] Imbalance detection useful and accurate
- [ ] Intensity distribution analysis complete
- [ ] Adherence tracking correct
- [ ] Comparisons work for multiple entities
- [ ] All insights performant (<500ms)

---

### Phase 4: Search, Discovery & Session Lifecycle 🔍

**Goal**: Improve discoverability and workout tracking

**Tasks**:
- [14-text-search-implementation.md](./14-text-search-implementation.md) - Search exercises and routines
- [15-exercise-discovery.md](./15-exercise-discovery.md) - Recent, unused, by equipment
- [16-routine-discovery.md](./16-routine-discovery.md) - By muscle group, recently used
- [17-session-lifecycle-enhancement.md](./17-session-lifecycle-enhancement.md) - Active session, progress
- [18-phase4-integration-testing.md](./18-phase4-integration-testing.md) - Comprehensive Phase 4 validation

**Success Criteria**:
- [ ] Search works with partial matches (case-insensitive)
- [ ] Discovery queries useful
- [ ] Session lifecycle tracking works
- [ ] Active session management functional
- [ ] Performance acceptable (<200ms for search)

---

### Phase 5: Bodyweight & Composition Analytics ⚖️

**Goal**: Complete bodyweight tracking with analytics

**Tasks**:
- [19-bodyweight-trend-analysis.md](./19-bodyweight-trend-analysis.md) - Trends, moving averages
- [20-bodyweight-goal-tracking.md](./20-bodyweight-goal-tracking.md) - Goal CRUD and progress
- [21-weight-change-rate.md](./21-weight-change-rate.md) - Rate analysis and recommendations
- [22-bodyweight-correlations.md](./22-bodyweight-correlations.md) - Weight vs strength/volume
- [23-phase5-integration-testing.md](./23-phase5-integration-testing.md) - Comprehensive Phase 5 validation

**Success Criteria**:
- [ ] Trend analysis accurate with moving averages
- [ ] Goal tracking intuitive with progress projections
- [ ] Rate analysis provides useful recommendations
- [ ] Correlation analysis reveals patterns

---

### Phase 6: Feedback & Final Polish 🎨

**Goal**: Add feedback system and finalize for production

**Tasks**:
- [24-session-feedback-system.md](./24-session-feedback-system.md) - Difficulty, enjoyment, energy ratings
- [25-calendar-enhancements.md](./25-calendar-enhancements.md) - Weekly view, missed sessions
- [26-comprehensive-integration-testing.md](./26-comprehensive-integration-testing.md) - End-to-end workflows
- [27-performance-optimization.md](./27-performance-optimization.md) - Query optimization, indexing
- [28-documentation-cleanup.md](./28-documentation-cleanup.md) - Update AGENTS.md, DESIGN.md

**Success Criteria**:
- [ ] Feedback system functional and useful
- [ ] Calendar enhanced with adherence tracking
- [ ] All integration tests pass
- [ ] Performance optimized (all queries <500ms)
- [ ] Documentation complete and accurate

---

## Current State Analysis

### What Works ✅
- Core CRUD for exercises, routines, mesocycles, sessions, bodyweight
- Basic pagination infrastructure
- Clean Architecture with proper layering
- GraphQL API with Strawberry
- Authentication middleware
- SQLAlchemy async repositories with UoW pattern
- Basic insights (volume, intensity, progressive overload)
- Calendar queries (day, range)

### What's Broken ❌
- Session filtering (status, mesocycle_id, date_from, date_to) - **defined but not implemented**
- Bodyweight date filtering - **defined but not implemented**
- Exercise history returns empty exercise arrays - **bug in insight service**

### What's Missing 🚧
- Personal records tracking
- Exercise trend analysis
- Muscle group imbalance detection
- Intensity distribution analysis
- Mesocycle adherence tracking
- Comparison & benchmarking
- Text search functionality
- Exercise/routine discovery queries
- Session lifecycle tracking
- Bodyweight analytics (trends, goals, correlations)
- Session feedback system
- Enhanced calendar features

---

## Architecture Patterns to Follow

### Service Layer Pattern
```python
async def method_name(self, params) -> ReturnDTO:
    async with self.uow:
        # 1. Fetch data from repository
        # 2. Apply business logic
        # 3. Commit if write operation
        # 4. Return DTO
```

### Repository Layer Pattern
```python
async def list_by_filters(
    self, field: Type | None = None, offset: int = 0, limit: int = 20
) -> Sequence[Entity]:
    stmt = select(Table).options(selectinload(...))
    filters = []
    if field: filters.append(Table.field == field)
    if filters: stmt = stmt.where(and_(*filters))
    # Execute and return domain entities
```

### Testing Pattern (AAA)
```python
@pytest.mark.asyncio
async def test_feature_success(service, mock_uow):
    # Arrange: Set up mocks and data
    # Act: Call service method
    # Assert: Verify results and mock calls
```

---

## Success Metrics

### Code Quality
- ✅ 100% type hint coverage
- ✅ ≥85% test coverage on service layer
- ✅ All tests passing
- ✅ No linting errors (`uv run ruff check .`)
- ✅ Properly formatted (`uv run ruff format .`)

### Performance
- ✅ List queries <200ms
- ✅ Complex analytics <500ms
- ✅ Search queries <200ms
- ✅ No N+1 query issues

### Documentation
- ✅ All business logic commented
- ✅ Calculation formulas documented
- ✅ AGENTS.md updated
- ✅ DESIGN.md updated
- ✅ GraphQL schema exported

---

## Risk Mitigation

### Potential Risks
1. **Performance Issues**: Regular testing, proactive indexing, dedicated optimization phase
2. **Test Complexity**: Use factories, create helpers, subagent debugging
3. **Scope Creep**: Stick to defined features, document "nice-to-haves" separately
4. **Integration Issues**: Frequent integration testing, buffer time in Phase 6

### Contingency Plans
- Performance issues → Dedicated optimization in Phase 6
- Test failures → Subagent assignment for deep debugging
- Timeline pressure → De-scope less critical features
- Integration problems → Additional buffer time allocated

---

## Getting Started

### Prerequisites
- All existing tests passing: `uv run pytest`
- Clean git working directory
- Development environment configured

### Starting Phase 1
1. Read [01-fix-session-filtering.md](./01-fix-session-filtering.md)
2. Create feature branch: `git checkout -b feature/phase1-filtering`
3. Follow task instructions
4. Run tests after each task
5. Commit incrementally

### Command Reference
```bash
# Run all tests
uv run pytest

# Run with minimal output
uv run pytest -q --tb=short --disable-warnings

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

# Run specific test
uv run pytest tests/integration/test_file.py -k test_name -vv

# Lint check
uv run ruff check .

# Format code
uv run ruff format .

# Export GraphQL schema
PYTHONPATH=src uv run python src/export_schema.py > schema.graphql
```

---

## Questions or Issues?

If you encounter any issues during implementation:
1. Review the specific task document
2. Check the codebase patterns (service/repository examples)
3. Run tests to identify the issue
4. Use subagent for deep debugging if needed
5. Document any deviations from the plan

---

**Ready to begin?** Start with [Phase 1, Task 01: Fix Session Filtering](./01-fix-session-filtering.md)
