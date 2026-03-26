# Task 06: Exercise Trend Analysis

**Status**: Not Started
**Priority**: High
**Estimated Effort**: 6-8 hours
**Dependencies**: Task 05 (Personal Records)
**Assigned To**: TBD

---

## User Story

**As a** serious lifter
**I want to** see a graph of my estimated 1RM and max weight for specific exercises over time
**So that** I can visualize my strength gains and ensure my training program is effective.

---

## Background

While Personal Records (Task 05) show the absolute best performance, **Trend Analysis** shows the trajectory of performance. It helps users see if they are plateauing, improving, or regressing. The most common metric for strength trends is **Estimated 1RM (e1RM)** using formulas like Epley or Brzycki, as users rarely test true 1RM frequently.

**Key Metrics**:
- **Estimated 1RM (e1RM)**: Calculated for every session using the best set (Max Weight x Reps).
- **Max Weight**: The heaviest weight handled in a session (regardless of reps).

**Scope**:
- Backend support for querying historical e1RM and Max Weight data points.
- Flexible date ranges.
- Handling different rep ranges (e.g., e1RM is less accurate for high reps, so maybe filter or flag).

---

## Acceptance Criteria

### Functional Requirements

- [ ] **AC1**: GraphQL query `exercisePerformanceTrend` accepts `exerciseId`, `dateFrom`, `dateTo`, and `metric` (Enum: `E1RM`, `MAX_WEIGHT`).
- [ ] **AC2**: Returns a list of data points `(date, value, actual_weight, actual_reps)` for each session in the range.
- [ ] **AC3**: **e1RM Calculation**: Uses the **Epley Formula** (`weight * (1 + reps/30)`) by default.
- [ ] **AC4**: For e1RM metric, selects the *best* set of the session (highest calculated e1RM) to represent that day.
- [ ] **AC5**: For Max Weight metric, selects the heaviest successful set (reps > 0) of the session.
- [ ] **AC6**: Handles sessions where the exercise was performed multiple times (uses best performance).
- [ ] **AC7**: Returns empty list if no data found in range.
- [ ] **AC8**: Validates date range (max 1 year).

### Non-Functional Requirements

- [ ] **NFR1**: Query execution < 400ms.
- [ ] **NFR2**: Logic resides in `InsightService` (Application Layer).
- [ ] **NFR3**: Formulas are encapsulated in a Domain Service or Helper.

---

## Implementation Plan

### 1. Domain Layer Updates

#### 1.1 Add e1RM Calculation Logic (`src/app/domain/services/strength_formulas.py`)
Create a pure domain service/helper for standard strength formulas.

```python
def calculate_epley_1rm(weight: float, reps: int) -> float:
    """
    Calculates Estimated 1RM using Epley formula.
    1RM = w * (1 + r/30)
    """
    if reps == 1:
        return weight
    return weight * (1 + reps / 30.0)
```

#### 1.2 Update DTOs (`src/app/application/dtos/insight.py`)

```python
@dataclass(frozen=True)
class TrendDataPoint:
    date: date
    value: float  # The e1RM or Max Weight value
    source_weight: float  # The actual weight used
    source_reps: int  # The actual reps performed
    set_id: UUID  # Reference to the specific set

@dataclass(frozen=True)
class ExerciseTrendDTO:
    exercise_id: UUID
    metric: str  # "E1RM" or "MAX_WEIGHT"
    data_points: list[TrendDataPoint]
```

### 2. Service Layer Implementation (`src/app/application/services/insight_service.py`)

Implement `get_exercise_performance_trend` method.

- Fetch sessions/exercises within date range (reuse repo method from Task 05/07 if suitable, or `get_by_date_range`).
- Iterate through sessions:
  - For each session, find all sets for the target exercise.
  - **For e1RM**: Calculate e1RM for every valid set. Pick the max.
  - **For Max Weight**: Pick the max `actual_weight_kg`.
- Construct `TrendDataPoint`.
- Sort by date.

### 3. Presentation Layer (GraphQL)

#### 3.1 Schema Definition

```graphql
enum TrendMetric {
    E1RM
    MAX_WEIGHT
}

type TrendDataPoint {
    date: Date!
    value: Float!
    sourceWeight: Float!
    sourceReps: Int!
}

type ExerciseTrend {
    exerciseId: ID!
    metric: TrendMetric!
    dataPoints: [TrendDataPoint!]!
}

extend type Query {
    exercisePerformanceTrend(
        exerciseId: ID!, 
        dateFrom: Date!, 
        dateTo: Date!, 
        metric: TrendMetric!
    ): ExerciseTrend!
}
```

#### 3.2 Resolver

Maps the DTO to GraphQL types. Handles Enum conversion.

### 4. Testing

- **Unit Tests**:
  - Test e1RM formula accuracy.
  - Test selection logic (picking the best set out of multiple sets/sessions).
  - Test date range filtering.
- **Integration Tests**:
  - Create sessions with varying weights/reps.
  - Query `exercisePerformanceTrend`.
  - Verify correct values are returned.

---

## Technical Considerations

- **Performance**: Fetching all sets for a year might be heavy if not optimized. Ensure the repository query loads only necessary data (or use a specialized query if needed, though app-side filtering is fine for typical user volumes).
- **Outliers**: High rep sets (e.g., 20 reps) yield inaccurate e1RM.
  - *Decision*: Include all valid sets for now. Future enhancement: add `maxReps` filter (e.g., ignore sets > 12 reps for 1RM calc).
- **Failed Sets**: Sets with `0` reps should be ignored.

## Files to Create/Modify

1.  `src/app/domain/services/strength_formulas.py` (New)
2.  `src/app/application/dtos/insight.py` (Modify)
3.  `src/app/application/services/insight_service.py` (Modify)
4.  `src/app/presentation/graphql/types/insight.py` (Modify)
5.  `src/app/presentation/graphql/resolvers/insight.py` (Modify)
6.  `tests/unit/domain/test_strength_formulas.py` (New)
7.  `tests/integration/test_insight_trend.py` (New)
