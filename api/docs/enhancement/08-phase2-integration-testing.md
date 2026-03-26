# Task 08: Phase 2 Integration Testing

**Status**: Not Started
**Priority**: Medium
**Estimated Effort**: 4-6 hours
**Dependencies**: Tasks 05, 06, 07
**Assigned To**: TBD

---

## Objective

Ensure all Phase 2 analytics features (Personal Records, Trends, Volume Progression) work correctly in isolation and together, are performant, and handle edge cases robustly. This phase focuses on the "holistic" correctness of the Insights module.

## Scope

1.  **End-to-End Scenarios**: Simulating a user's journey over several months of training.
2.  **Performance Testing**: Verifying query response times with realistic data volumes (1 year of history).
3.  **Regression Testing**: Ensuring existing features (Session logging) still work and correctly feed into the new analytics.
4.  **Edge Case validation**: Partial data, deleted sessions, re-ordered sets.

---

## Test Scenarios

### 1. The "New Lifter" Journey (Progression)

**Scenario**: A user starts with empty data and logs sessions over 4 weeks.
- **Week 1**: Bench Press 50kg.
  - Verify: PR is 50kg. Volume is calculated correctly. Trend shows 1 point.
- **Week 2**: Bench Press 55kg.
  - Verify: PR updates to 55kg. Volume increases. Trend shows upward slope.
- **Week 3**: Bench Press 52.5kg (Bad day).
  - Verify: PR remains 55kg. Volume recorded. Trend shows dip or plateau.
- **Week 4**: Bench Press 60kg.
  - Verify: PR updates to 60kg.

**Test Implementation**:
- Create a specialized integration test file: `tests/integration/scenarios/test_phase2_user_journey.py`.
- Use the `client` to make GraphQL mutations (log sessions) and queries (get insights) sequentially.

### 2. The "Data Correction" Scenario

**Scenario**: A user logs a session with a typo (e.g., 500kg instead of 50kg) and then fixes it.
- **Action**: User logs 500kg Squat.
- **Check**: PR is 500kg (Incorrect).
- **Action**: User updates session set to 50kg.
- **Check**: PR recalculates to correct max (e.g., previous max or 50kg).
  - *Note*: This verifies that the PR system isn't "append-only" and correctly reflects current state.

### 3. Performance & Volume Load

**Scenario**: User has 150 sessions (3/week for a year) with 5 exercises each.
- **Action**: Query `exercisePerformanceTrend` for the whole year.
- **Action**: Query `exerciseVolumeProgression` for the whole year.
- **Expectation**: Response time < 500ms.
- **Test Implementation**:
  - Use `factory_boy` or a loop to seed database with 150 sessions.
  - Measure execution time of the GraphQL query.

### 4. Cross-Feature consistency

**Scenario**: Verify that the "Max Weight" in Trend Analysis matches the "Personal Record" value for the same date.
- **Check**: `exercisePerformanceTrend` max value == `personalRecords` value.

---

## Implementation Plan

### 1. Create Scenario Tests (`tests/integration/scenarios/`)

Create `test_phase2_analytics_journey.py`:
- Use `pytest-asyncio`.
- Helper functions to log sessions quickly.
- Assertions for Insights queries.

### 2. Create Performance Tests (`tests/performance/`)

Create `test_analytics_performance.py`:
- **Seed**: Generate 365 days of data for a specific user/exercise.
- **Measure**: Time the `insight_service.get_...` calls.
- **Fail Criteria**: If execution > 500ms (soft limit) or 1s (hard limit).

### 3. Manual Verification Script

Create a script `scripts/verify_phase2.py`:
- Can be run against a local dev DB.
- Prints out a summary of PRs and Trends for a specific user to console for visual inspection.

---

## Success Criteria

- [ ] All new scenario tests pass.
- [ ] Performance tests demonstrate < 500ms response times for 1 year of data.
- [ ] No regressions in Phase 1 tests.
- [ ] "Data Correction" scenario passes (updates to sessions reflect in analytics).

## Files to Create

1.  `tests/integration/scenarios/test_phase2_analytics_journey.py`
2.  `tests/performance/test_analytics_performance.py`
3.  `scripts/verify_phase2.py` (Optional but recommended)
