# Task 07: Exercise Volume Progression

**Status**: Not Started  
**Priority**: High  
**Estimated Effort**: 6-8 hours  
**Dependencies**: Tasks 05 (Performance Trends), 06 (Exercise PRs)  
**Assigned To**: TBD

---

## User Story

**As a** strength training user  
**I want to** see how my training volume has progressed for each exercise over time  
**So that** I can ensure I'm applying progressive overload principles and identify volume trends, plateaus, or deloads.

---

## Background

Training volume (sets × reps × weight) is one of the most important metrics for progressive overload and hypertrophy. This task implements comprehensive volume tracking and progression analysis for individual exercises.

**Key Concepts**:
- **Set Volume**: `reps × weight_kg` for a single set
- **Session Volume**: Sum of all set volumes for an exercise in a session
- **Weekly Volume**: Sum of session volumes across a week
- **Volume Progression**: Change in volume over time (weekly, monthly, mesocycle)

**Use Cases**:
1. User wants to see if weekly volume is increasing for Squats over 12 weeks
2. User identifies a deload week with intentionally reduced volume
3. User compares volume between mesocycles to plan next training phase
4. User spots a plateau and adjusts programming

---

## Acceptance Criteria

### Functional Requirements

- [ ] **AC1**: GraphQL query `exerciseVolumeProgression` accepts `exerciseId`, `dateFrom`, and `dateTo`
- [ ] **AC2**: Returns weekly volume data points when date range > 30 days
- [ ] **AC3**: Returns daily volume data points when date range ≤ 30 days
- [ ] **AC4**: Each data point includes: date, total_volume, total_sets, avg_intensity, session_count
- [ ] **AC5**: Response includes total volume change percentage (first period vs last period)
- [ ] **AC6**: Response includes average volume per period
- [ ] **AC7**: Response identifies peak week/day (highest volume)
- [ ] **AC8**: Response identifies lowest week/day (lowest volume, excluding zeros)
- [ ] **AC9**: Handles incomplete sets (missing reps/weight) by skipping them
- [ ] **AC10**: Includes zero-volume periods (deload weeks) in the data
- [ ] **AC11**: Limits date range to maximum 1 year
- [ ] **AC12**: Returns empty data_points if no sessions found in range

### Non-Functional Requirements

- [ ] **NFR1**: Query executes in <500ms for 1 year of data
- [ ] **NFR2**: Repository uses efficient date filtering and indexing
- [ ] **NFR3**: Service layer uses proper grouping algorithms (defaultdict)
- [ ] **NFR4**: 100% type hint coverage
- [ ] **NFR5**: All calculations use UTC timestamps

---

## Implementation Plan

### 1. Domain Layer Updates

#### 1.1 Create DTOs (`src/app/application/dtos/insights.py`)

```python
from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class VolumeDataPoint:
    """Represents volume metrics for a specific time period."""
    
    date: date  # Start of week or specific day
    total_volume: float  # sum(sets × reps × weight)
    total_sets: int  # Total sets performed
    avg_intensity: float  # Average weight across all sets
    session_count: int  # Number of times exercise was performed
    
    def __post_init__(self):
        """Validate data point."""
        if self.total_volume < 0:
            raise ValueError("total_volume cannot be negative")
        if self.total_sets < 0:
            raise ValueError("total_sets cannot be negative")
        if self.avg_intensity < 0:
            raise ValueError("avg_intensity cannot be negative")
        if self.session_count < 0:
            raise ValueError("session_count cannot be negative")


@dataclass(frozen=True)
class ExerciseVolumeProgressionDTO:
    """Volume progression analytics for a specific exercise over time."""
    
    exercise_id: UUID
    exercise_name: str
    date_from: date
    date_to: date
    data_points: list[VolumeDataPoint]  # Ordered chronologically
    total_volume_change_pct: float | None  # None if <2 data points
    avg_weekly_volume: float  # Average across all periods
    peak_week: VolumeDataPoint | None  # Highest volume period
    lowest_week: VolumeDataPoint | None  # Lowest non-zero volume period
    granularity: str  # "daily" or "weekly"
    
    def __post_init__(self):
        """Validate progression data."""
        if self.date_from > self.date_to:
            raise ValueError("date_from must be before date_to")
        
        # Validate data_points are ordered
        for i in range(len(self.data_points) - 1):
            if self.data_points[i].date >= self.data_points[i + 1].date:
                raise ValueError("data_points must be ordered chronologically")
```

### 2. Service Layer Implementation

#### 2.1 Add Method to `InsightService` (`src/app/application/services/insight_service.py`)

```python
from collections import defaultdict
from datetime import date, datetime, timedelta, UTC
from typing import Any

async def get_exercise_volume_progression(
    self,
    exercise_id: UUID,
    date_from: date,
    date_to: date,
) -> ExerciseVolumeProgressionDTO:
    """
    Calculate volume progression for an exercise over time.
    
    Args:
        exercise_id: UUID of the exercise to analyze
        date_from: Start date (inclusive)
        date_to: End date (inclusive)
        
    Returns:
        ExerciseVolumeProgressionDTO with volume progression data
        
    Raises:
        ValueError: If date range exceeds 365 days
        EntityNotFoundError: If exercise doesn't exist
    """
    # Validate date range
    if (date_to - date_from).days > 365:
        raise ValueError("Date range cannot exceed 365 days")
    
    # Fetch exercise to get name
    exercise = await self.uow.exercises.get_by_id(exercise_id)
    if not exercise:
        raise EntityNotFoundError(f"Exercise {exercise_id} not found")
    
    # Determine granularity
    date_range_days = (date_to - date_from).days
    granularity = "daily" if date_range_days <= 30 else "weekly"
    
    # Fetch all completed sessions in date range
    sessions = await self.uow.sessions.get_by_date_range(
        date_from=date_from,
        date_to=date_to,
        status=SessionStatus.COMPLETED
    )
    
    # Group sessions by exercise and time period
    volume_by_period: dict[date, dict[str, Any]] = defaultdict(
        lambda: {
            "total_volume": 0.0,
            "total_sets": 0,
            "total_weight_sum": 0.0,  # For avg intensity calculation
            "session_count": 0,
            "sessions_seen": set(),  # Track unique sessions
        }
    )
    
    for session in sessions:
        # Find exercises in this session
        for session_exercise in session.exercises:
            if session_exercise.exercise_id != exercise_id:
                continue
            
            # Determine period key (week start or day)
            session_date = session.started_at.date()
            if granularity == "weekly":
                period_key = _get_week_start(session_date)
            else:
                period_key = session_date
            
            period_data = volume_by_period[period_key]
            
            # Track unique sessions
            if session.id not in period_data["sessions_seen"]:
                period_data["sessions_seen"].add(session.id)
                period_data["session_count"] += 1
            
            # Calculate volume for this session_exercise
            for set_item in session_exercise.sets:
                # Skip incomplete sets
                if (set_item.actual_reps is None or 
                    set_item.actual_weight_kg is None or
                    set_item.actual_reps <= 0 or
                    set_item.actual_weight_kg < 0):
                    continue
                
                set_volume = set_item.actual_reps * set_item.actual_weight_kg
                period_data["total_volume"] += set_volume
                period_data["total_sets"] += 1
                period_data["total_weight_sum"] += set_item.actual_weight_kg
    
    # Convert to data points
    data_points: list[VolumeDataPoint] = []
    for period_date in sorted(volume_by_period.keys()):
        period_data = volume_by_period[period_date]
        
        # Calculate avg intensity
        avg_intensity = (
            period_data["total_weight_sum"] / period_data["total_sets"]
            if period_data["total_sets"] > 0
            else 0.0
        )
        
        data_points.append(
            VolumeDataPoint(
                date=period_date,
                total_volume=period_data["total_volume"],
                total_sets=period_data["total_sets"],
                avg_intensity=avg_intensity,
                session_count=period_data["session_count"],
            )
        )
    
    # Fill in zero-volume periods if needed
    if granularity == "weekly":
        data_points = _fill_missing_weeks(data_points, date_from, date_to)
    # For daily, we don't fill gaps as they're expected
    
    # Calculate summary statistics
    volume_change_pct = _calculate_volume_change(data_points)
    avg_weekly_volume = (
        sum(dp.total_volume for dp in data_points) / len(data_points)
        if data_points
        else 0.0
    )
    peak_week = _find_peak_week(data_points)
    lowest_week = _find_lowest_week(data_points)
    
    return ExerciseVolumeProgressionDTO(
        exercise_id=exercise_id,
        exercise_name=exercise.name,
        date_from=date_from,
        date_to=date_to,
        data_points=data_points,
        total_volume_change_pct=volume_change_pct,
        avg_weekly_volume=avg_weekly_volume,
        peak_week=peak_week,
        lowest_week=lowest_week,
        granularity=granularity,
    )


def _get_week_start(d: date) -> date:
    """Get the Monday of the week containing the given date."""
    # ISO calendar: Monday = 1, Sunday = 7
    weekday = d.isoweekday()
    days_since_monday = weekday - 1
    return d - timedelta(days=days_since_monday)


def _fill_missing_weeks(
    data_points: list[VolumeDataPoint],
    date_from: date,
    date_to: date,
) -> list[VolumeDataPoint]:
    """Fill in missing weeks with zero-volume data points."""
    if not data_points:
        return []
    
    filled: list[VolumeDataPoint] = []
    current_date = _get_week_start(date_from)
    end_date = _get_week_start(date_to)
    
    # Create a map for quick lookup
    data_map = {dp.date: dp for dp in data_points}
    
    while current_date <= end_date:
        if current_date in data_map:
            filled.append(data_map[current_date])
        else:
            # Add zero-volume week
            filled.append(
                VolumeDataPoint(
                    date=current_date,
                    total_volume=0.0,
                    total_sets=0,
                    avg_intensity=0.0,
                    session_count=0,
                )
            )
        current_date += timedelta(days=7)
    
    return filled


def _calculate_volume_change(data_points: list[VolumeDataPoint]) -> float | None:
    """Calculate percentage change from first to last period."""
    if len(data_points) < 2:
        return None
    
    first_volume = data_points[0].total_volume
    last_volume = data_points[-1].total_volume
    
    if first_volume == 0:
        return None  # Can't calculate % change from zero
    
    return ((last_volume - first_volume) / first_volume) * 100


def _find_peak_week(data_points: list[VolumeDataPoint]) -> VolumeDataPoint | None:
    """Find the data point with the highest total volume."""
    if not data_points:
        return None
    
    return max(data_points, key=lambda dp: dp.total_volume)


def _find_lowest_week(data_points: list[VolumeDataPoint]) -> VolumeDataPoint | None:
    """Find the data point with the lowest non-zero total volume."""
    non_zero = [dp for dp in data_points if dp.total_volume > 0]
    if not non_zero:
        return None
    
    return min(non_zero, key=lambda dp: dp.total_volume)
```

### 3. Repository Layer Updates

#### 3.1 Add Method to `SessionRepository` (`src/app/infrastructure/repositories/session_repository.py`)

```python
async def get_by_date_range(
    self,
    date_from: date,
    date_to: date,
    status: SessionStatus | None = None,
) -> list[WorkoutSession]:
    """
    Fetch sessions within a date range.
    
    Args:
        date_from: Start date (inclusive)
        date_to: End date (inclusive)
        status: Optional status filter
        
    Returns:
        List of sessions ordered by started_at
    """
    from datetime import datetime, UTC, time
    
    # Convert dates to datetime (start of day, end of day)
    dt_from = datetime.combine(date_from, time.min, tzinfo=UTC)
    dt_to = datetime.combine(date_to, time.max, tzinfo=UTC)
    
    stmt = (
        select(SessionModel)
        .where(
            SessionModel.started_at >= dt_from,
            SessionModel.started_at <= dt_to,
        )
        .options(
            selectinload(SessionModel.exercises).selectinload(
                SessionExerciseModel.sets
            )
        )
        .order_by(SessionModel.started_at)
    )
    
    if status:
        stmt = stmt.where(SessionModel.status == status.value)
    
    result = await self.session.execute(stmt)
    session_models = result.scalars().all()
    
    return [self._to_entity(model) for model in session_models]
```

#### 3.2 Update `ISessionRepository` Interface (`src/app/domain/repositories/session_repository.py`)

```python
from abc import ABC, abstractmethod
from datetime import date

class ISessionRepository(ABC):
    # ... existing methods ...
    
    @abstractmethod
    async def get_by_date_range(
        self,
        date_from: date,
        date_to: date,
        status: SessionStatus | None = None,
    ) -> list[WorkoutSession]:
        """Fetch sessions within a date range."""
        pass
```

### 4. Presentation Layer (GraphQL)

#### 4.1 Add GraphQL Types (`src/app/presentation/graphql/types/insights.py`)

```python
import strawberry
from datetime import date


@strawberry.type
class VolumeDataPoint:
    """Volume metrics for a specific time period."""
    
    date: date
    total_volume: float
    total_sets: int
    avg_intensity: float
    session_count: int


@strawberry.type
class ExerciseVolumeProgression:
    """Volume progression analytics for an exercise over time."""
    
    exercise_id: strawberry.ID
    exercise_name: str
    date_from: date
    date_to: date
    data_points: list[VolumeDataPoint]
    total_volume_change_pct: float | None
    avg_weekly_volume: float
    peak_week: VolumeDataPoint | None
    lowest_week: VolumeDataPoint | None
    granularity: str
```

#### 4.2 Add Resolver (`src/app/presentation/graphql/resolvers/insights.py`)

```python
@strawberry.field
async def exercise_volume_progression(
    self,
    info: Info,
    exercise_id: strawberry.ID,
    date_from: date,
    date_to: date,
) -> ExerciseVolumeProgression:
    """
    Get volume progression for an exercise over time.
    
    Args:
        exercise_id: UUID of the exercise
        date_from: Start date (inclusive)
        date_to: End date (inclusive)
        
    Returns:
        Volume progression data with weekly/daily granularity
        
    Raises:
        ValueError: If date range exceeds 365 days
        EntityNotFoundError: If exercise not found
    """
    uow = get_uow(info)
    service = InsightService(uow)
    
    try:
        exercise_uuid = UUID(exercise_id)
    except ValueError as e:
        raise ValueError(f"Invalid exercise_id format: {e}")
    
    dto = await service.get_exercise_volume_progression(
        exercise_id=exercise_uuid,
        date_from=date_from,
        date_to=date_to,
    )
    
    # Convert DTO to GraphQL type
    return ExerciseVolumeProgression(
        exercise_id=strawberry.ID(str(dto.exercise_id)),
        exercise_name=dto.exercise_name,
        date_from=dto.date_from,
        date_to=dto.date_to,
        data_points=[
            VolumeDataPoint(
                date=dp.date,
                total_volume=dp.total_volume,
                total_sets=dp.total_sets,
                avg_intensity=dp.avg_intensity,
                session_count=dp.session_count,
            )
            for dp in dto.data_points
        ],
        total_volume_change_pct=dto.total_volume_change_pct,
        avg_weekly_volume=dto.avg_weekly_volume,
        peak_week=(
            VolumeDataPoint(
                date=dto.peak_week.date,
                total_volume=dto.peak_week.total_volume,
                total_sets=dto.peak_week.total_sets,
                avg_intensity=dto.peak_week.avg_intensity,
                session_count=dto.peak_week.session_count,
            )
            if dto.peak_week
            else None
        ),
        lowest_week=(
            VolumeDataPoint(
                date=dto.lowest_week.date,
                total_volume=dto.lowest_week.total_volume,
                total_sets=dto.lowest_week.total_sets,
                avg_intensity=dto.lowest_week.avg_intensity,
                session_count=dto.lowest_week.session_count,
            )
            if dto.lowest_week
            else None
        ),
        granularity=dto.granularity,
    )
```

#### 4.3 Register Query in Schema (`src/app/presentation/graphql/schema.py`)

```python
@strawberry.type
class Query:
    # ... existing fields ...
    
    exercise_volume_progression: ExerciseVolumeProgression = strawberry.field(
        resolver=insights_resolver.exercise_volume_progression
    )
```

---

## Testing Strategy

### Unit Tests

#### Test File: `tests/unit/application/services/test_insight_service_volume.py`

```python
import pytest
from datetime import date, datetime, UTC, timedelta
from uuid import uuid4
from app.application.services.insight_service import InsightService
from app.application.dtos.insights import (
    ExerciseVolumeProgressionDTO,
    VolumeDataPoint,
)
from app.domain.entities.session import SessionStatus


@pytest.fixture
def mock_exercise():
    """Create a mock exercise."""
    return Exercise(
        id=uuid4(),
        name="Barbell Squat",
        description="Compound leg exercise",
        primary_muscle_group_id=uuid4(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_sessions_with_volume(mock_exercise):
    """Create mock sessions with volume data over 4 weeks."""
    sessions = []
    base_date = date(2026, 1, 6)  # Monday, Week 1
    
    # Week 1: 3 sessions, increasing volume
    for day_offset in [0, 2, 4]:  # Mon, Wed, Fri
        session_date = base_date + timedelta(days=day_offset)
        session = WorkoutSession(
            id=uuid4(),
            routine_id=uuid4(),
            started_at=datetime.combine(session_date, datetime.min.time(), UTC),
            status=SessionStatus.COMPLETED,
            exercises=[
                SessionExercise(
                    exercise_id=mock_exercise.id,
                    order=1,
                    sets=[
                        ExerciseSet(
                            set_number=1,
                            actual_reps=5,
                            actual_weight_kg=100.0,
                        ),
                        ExerciseSet(
                            set_number=2,
                            actual_reps=5,
                            actual_weight_kg=100.0,
                        ),
                        ExerciseSet(
                            set_number=3,
                            actual_reps=5,
                            actual_weight_kg=100.0,
                        ),
                    ],
                )
            ],
        )
        sessions.append(session)
    
    # Week 2: 3 sessions, higher volume
    for day_offset in [7, 9, 11]:
        session_date = base_date + timedelta(days=day_offset)
        session = WorkoutSession(
            id=uuid4(),
            routine_id=uuid4(),
            started_at=datetime.combine(session_date, datetime.min.time(), UTC),
            status=SessionStatus.COMPLETED,
            exercises=[
                SessionExercise(
                    exercise_id=mock_exercise.id,
                    order=1,
                    sets=[
                        ExerciseSet(set_number=1, actual_reps=5, actual_weight_kg=105.0),
                        ExerciseSet(set_number=2, actual_reps=5, actual_weight_kg=105.0),
                        ExerciseSet(set_number=3, actual_reps=5, actual_weight_kg=105.0),
                    ],
                )
            ],
        )
        sessions.append(session)
    
    # Week 3: Deload week (no sessions)
    
    # Week 4: 3 sessions, back to volume
    for day_offset in [21, 23, 25]:
        session_date = base_date + timedelta(days=day_offset)
        session = WorkoutSession(
            id=uuid4(),
            routine_id=uuid4(),
            started_at=datetime.combine(session_date, datetime.min.time(), UTC),
            status=SessionStatus.COMPLETED,
            exercises=[
                SessionExercise(
                    exercise_id=mock_exercise.id,
                    order=1,
                    sets=[
                        ExerciseSet(set_number=1, actual_reps=5, actual_weight_kg=110.0),
                        ExerciseSet(set_number=2, actual_reps=5, actual_weight_kg=110.0),
                        ExerciseSet(set_number=3, actual_reps=5, actual_weight_kg=110.0),
                    ],
                )
            ],
        )
        sessions.append(session)
    
    return sessions


class TestExerciseVolumeProgression:
    """Test volume progression calculations."""
    
    async def test_weekly_volume_progression_basic(
        self, mock_uow, mock_exercise, mock_sessions_with_volume
    ):
        """Test basic weekly volume progression calculation."""
        mock_uow.exercises.get_by_id.return_value = mock_exercise
        mock_uow.sessions.get_by_date_range.return_value = mock_sessions_with_volume
        
        service = InsightService(mock_uow)
        
        result = await service.get_exercise_volume_progression(
            exercise_id=mock_exercise.id,
            date_from=date(2026, 1, 6),
            date_to=date(2026, 2, 2),  # 4 weeks
        )
        
        assert result.exercise_id == mock_exercise.id
        assert result.exercise_name == "Barbell Squat"
        assert result.granularity == "weekly"
        assert len(result.data_points) == 4  # 4 weeks including deload
        
        # Week 1: 3 sessions × 3 sets × 5 reps × 100kg = 4500kg
        assert result.data_points[0].total_volume == 4500.0
        assert result.data_points[0].total_sets == 9
        assert result.data_points[0].session_count == 3
        assert result.data_points[0].avg_intensity == 100.0
        
        # Week 2: 3 sessions × 3 sets × 5 reps × 105kg = 4725kg
        assert result.data_points[1].total_volume == 4725.0
        
        # Week 3: Deload (zero volume)
        assert result.data_points[2].total_volume == 0.0
        assert result.data_points[2].session_count == 0
        
        # Week 4: 3 sessions × 3 sets × 5 reps × 110kg = 4950kg
        assert result.data_points[3].total_volume == 4950.0
        
        # Volume change: (4950 - 4500) / 4500 * 100 = 10%
        assert result.total_volume_change_pct == pytest.approx(10.0)
        
        # Peak week should be Week 4
        assert result.peak_week.total_volume == 4950.0
        
        # Lowest week should be Week 1 (excluding zero-volume Week 3)
        assert result.lowest_week.total_volume == 4500.0
    
    async def test_daily_granularity_short_range(self, mock_uow, mock_exercise):
        """Test daily granularity for date ranges ≤30 days."""
        # Create 2 weeks of data
        sessions = []
        base_date = date(2026, 1, 6)
        
        for day in range(14):
            if day % 2 == 0:  # Every other day
                session_date = base_date + timedelta(days=day)
                session = WorkoutSession(
                    id=uuid4(),
                    routine_id=uuid4(),
                    started_at=datetime.combine(session_date, datetime.min.time(), UTC),
                    status=SessionStatus.COMPLETED,
                    exercises=[
                        SessionExercise(
                            exercise_id=mock_exercise.id,
                            order=1,
                            sets=[
                                ExerciseSet(
                                    set_number=1,
                                    actual_reps=10,
                                    actual_weight_kg=50.0,
                                ),
                            ],
                        )
                    ],
                )
                sessions.append(session)
        
        mock_uow.exercises.get_by_id.return_value = mock_exercise
        mock_uow.sessions.get_by_date_range.return_value = sessions
        
        service = InsightService(mock_uow)
        
        result = await service.get_exercise_volume_progression(
            exercise_id=mock_exercise.id,
            date_from=base_date,
            date_to=base_date + timedelta(days=13),
        )
        
        assert result.granularity == "daily"
        assert len(result.data_points) == 7  # 7 training days
        
        # Each day: 1 set × 10 reps × 50kg = 500kg
        for dp in result.data_points:
            assert dp.total_volume == 500.0
            assert dp.session_count == 1
    
    async def test_handles_incomplete_sets(self, mock_uow, mock_exercise):
        """Test that incomplete sets are skipped."""
        session = WorkoutSession(
            id=uuid4(),
            routine_id=uuid4(),
            started_at=datetime.now(UTC),
            status=SessionStatus.COMPLETED,
            exercises=[
                SessionExercise(
                    exercise_id=mock_exercise.id,
                    order=1,
                    sets=[
                        # Complete set
                        ExerciseSet(
                            set_number=1,
                            actual_reps=10,
                            actual_weight_kg=50.0,
                        ),
                        # Missing reps
                        ExerciseSet(
                            set_number=2,
                            actual_reps=None,
                            actual_weight_kg=50.0,
                        ),
                        # Missing weight
                        ExerciseSet(
                            set_number=3,
                            actual_reps=10,
                            actual_weight_kg=None,
                        ),
                        # Zero reps (shouldn't count)
                        ExerciseSet(
                            set_number=4,
                            actual_reps=0,
                            actual_weight_kg=50.0,
                        ),
                        # Complete set
                        ExerciseSet(
                            set_number=5,
                            actual_reps=10,
                            actual_weight_kg=50.0,
                        ),
                    ],
                )
            ],
        )
        
        mock_uow.exercises.get_by_id.return_value = mock_exercise
        mock_uow.sessions.get_by_date_range.return_value = [session]
        
        service = InsightService(mock_uow)
        
        result = await service.get_exercise_volume_progression(
            exercise_id=mock_exercise.id,
            date_from=date.today(),
            date_to=date.today(),
        )
        
        # Only 2 complete sets should be counted
        assert len(result.data_points) == 1
        assert result.data_points[0].total_sets == 2
        assert result.data_points[0].total_volume == 1000.0  # 2 × 10 × 50
    
    async def test_no_sessions_in_range(self, mock_uow, mock_exercise):
        """Test handling of date range with no sessions."""
        mock_uow.exercises.get_by_id.return_value = mock_exercise
        mock_uow.sessions.get_by_date_range.return_value = []
        
        service = InsightService(mock_uow)
        
        result = await service.get_exercise_volume_progression(
            exercise_id=mock_exercise.id,
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 31),
        )
        
        assert len(result.data_points) == 0
        assert result.total_volume_change_pct is None
        assert result.avg_weekly_volume == 0.0
        assert result.peak_week is None
        assert result.lowest_week is None
    
    async def test_date_range_exceeds_365_days(self, mock_uow, mock_exercise):
        """Test that date ranges >365 days raise ValueError."""
        mock_uow.exercises.get_by_id.return_value = mock_exercise
        
        service = InsightService(mock_uow)
        
        with pytest.raises(ValueError, match="Date range cannot exceed 365 days"):
            await service.get_exercise_volume_progression(
                exercise_id=mock_exercise.id,
                date_from=date(2025, 1, 1),
                date_to=date(2026, 1, 2),  # 367 days
            )
    
    async def test_exercise_not_found(self, mock_uow):
        """Test handling of non-existent exercise."""
        mock_uow.exercises.get_by_id.return_value = None
        
        service = InsightService(mock_uow)
        
        with pytest.raises(EntityNotFoundError):
            await service.get_exercise_volume_progression(
                exercise_id=uuid4(),
                date_from=date(2026, 1, 1),
                date_to=date(2026, 1, 31),
            )
    
    async def test_single_data_point_no_change(self, mock_uow, mock_exercise):
        """Test that single data point returns None for volume change."""
        session = WorkoutSession(
            id=uuid4(),
            routine_id=uuid4(),
            started_at=datetime.now(UTC),
            status=SessionStatus.COMPLETED,
            exercises=[
                SessionExercise(
                    exercise_id=mock_exercise.id,
                    order=1,
                    sets=[
                        ExerciseSet(
                            set_number=1,
                            actual_reps=10,
                            actual_weight_kg=50.0,
                        ),
                    ],
                )
            ],
        )
        
        mock_uow.exercises.get_by_id.return_value = mock_exercise
        mock_uow.sessions.get_by_date_range.return_value = [session]
        
        service = InsightService(mock_uow)
        
        result = await service.get_exercise_volume_progression(
            exercise_id=mock_exercise.id,
            date_from=date.today(),
            date_to=date.today(),
        )
        
        assert len(result.data_points) == 1
        assert result.total_volume_change_pct is None  # Can't calculate with 1 point
```

### Integration Tests

#### Test File: `tests/integration/test_exercise_volume_progression.py`

```python
import pytest
from datetime import date, datetime, UTC, timedelta
from uuid import uuid4


@pytest.mark.asyncio
async def test_exercise_volume_progression_graphql(
    graphql_client,
    auth_headers,
    db_session,
    seed_muscle_groups,
):
    """Test exercise volume progression query via GraphQL."""
    # Create exercise
    exercise = await create_test_exercise(
        db_session,
        name="Barbell Bench Press",
        primary_muscle_group_id=seed_muscle_groups[0].id,
    )
    
    # Create mesocycle and routine
    mesocycle = await create_test_mesocycle(db_session, name="Test Meso")
    routine = await create_test_routine(
        db_session,
        mesocycle_id=mesocycle.id,
        name="Push Day",
    )
    
    # Create 4 weeks of sessions with progressive volume
    base_date = date(2026, 1, 6)
    
    for week in range(4):
        for day in [0, 2, 4]:  # Mon, Wed, Fri
            session_date = base_date + timedelta(weeks=week, days=day)
            weight = 100.0 + (week * 5)  # Progressive overload
            
            session = await create_test_session(
                db_session,
                routine_id=routine.id,
                started_at=datetime.combine(session_date, datetime.min.time(), UTC),
                status="COMPLETED",
            )
            
            await add_exercise_to_session(
                db_session,
                session_id=session.id,
                exercise_id=exercise.id,
                sets=[
                    {"set_number": 1, "actual_reps": 5, "actual_weight_kg": weight},
                    {"set_number": 2, "actual_reps": 5, "actual_weight_kg": weight},
                    {"set_number": 3, "actual_reps": 5, "actual_weight_kg": weight},
                ],
            )
    
    # Query volume progression
    query = """
        query ExerciseVolumeProgression(
            $exerciseId: ID!
            $dateFrom: Date!
            $dateTo: Date!
        ) {
            exerciseVolumeProgression(
                exerciseId: $exerciseId
                dateFrom: $dateFrom
                dateTo: $dateTo
            ) {
                exerciseId
                exerciseName
                dateFrom
                dateTo
                granularity
                dataPoints {
                    date
                    totalVolume
                    totalSets
                    avgIntensity
                    sessionCount
                }
                totalVolumeChangePct
                avgWeeklyVolume
                peakWeek {
                    date
                    totalVolume
                }
                lowestWeek {
                    date
                    totalVolume
                }
            }
        }
    """
    
    variables = {
        "exerciseId": str(exercise.id),
        "dateFrom": str(base_date),
        "dateTo": str(base_date + timedelta(days=27)),  # 4 weeks
    }
    
    response = await graphql_client.post(
        "/graphql",
        json={"query": query, "variables": variables},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()["data"]["exerciseVolumeProgression"]
    
    assert data["exerciseId"] == str(exercise.id)
    assert data["exerciseName"] == "Barbell Bench Press"
    assert data["granularity"] == "weekly"
    assert len(data["dataPoints"]) == 4
    
    # Week 1: 3 sessions × 3 sets × 5 reps × 100kg = 4500kg
    assert data["dataPoints"][0]["totalVolume"] == 4500.0
    assert data["dataPoints"][0]["totalSets"] == 9
    assert data["dataPoints"][0]["sessionCount"] == 3
    
    # Week 4: 3 sessions × 3 sets × 5 reps × 115kg = 5175kg
    assert data["dataPoints"][3]["totalVolume"] == 5175.0
    
    # Volume change: (5175 - 4500) / 4500 * 100 = 15%
    assert data["totalVolumeChangePct"] == pytest.approx(15.0)
    
    # Peak should be Week 4
    assert data["peakWeek"]["totalVolume"] == 5175.0
    
    # Lowest should be Week 1
    assert data["lowestWeek"]["totalVolume"] == 4500.0


@pytest.mark.asyncio
async def test_volume_progression_with_deload_week(
    graphql_client, auth_headers, db_session, seed_muscle_groups
):
    """Test volume progression correctly handles deload weeks."""
    exercise = await create_test_exercise(
        db_session,
        name="Deadlift",
        primary_muscle_group_id=seed_muscle_groups[0].id,
    )
    
    mesocycle = await create_test_mesocycle(db_session, name="Test Meso")
    routine = await create_test_routine(
        db_session, mesocycle_id=mesocycle.id, name="Pull Day"
    )
    
    base_date = date(2026, 1, 6)
    
    # Week 1: Normal volume
    for day in [0, 3]:  # Mon, Thu
        session_date = base_date + timedelta(days=day)
        session = await create_test_session(
            db_session,
            routine_id=routine.id,
            started_at=datetime.combine(session_date, datetime.min.time(), UTC),
            status="COMPLETED",
        )
        await add_exercise_to_session(
            db_session,
            session_id=session.id,
            exercise_id=exercise.id,
            sets=[
                {"set_number": 1, "actual_reps": 5, "actual_weight_kg": 140.0},
                {"set_number": 2, "actual_reps": 5, "actual_weight_kg": 140.0},
                {"set_number": 3, "actual_reps": 5, "actual_weight_kg": 140.0},
            ],
        )
    
    # Week 2: Deload (no sessions)
    
    # Week 3: Back to normal
    for day in [14, 17]:
        session_date = base_date + timedelta(days=day)
        session = await create_test_session(
            db_session,
            routine_id=routine.id,
            started_at=datetime.combine(session_date, datetime.min.time(), UTC),
            status="COMPLETED",
        )
        await add_exercise_to_session(
            db_session,
            session_id=session.id,
            exercise_id=exercise.id,
            sets=[
                {"set_number": 1, "actual_reps": 5, "actual_weight_kg": 145.0},
                {"set_number": 2, "actual_reps": 5, "actual_weight_kg": 145.0},
                {"set_number": 3, "actual_reps": 5, "actual_weight_kg": 145.0},
            ],
        )
    
    query = """
        query ExerciseVolumeProgression(
            $exerciseId: ID!
            $dateFrom: Date!
            $dateTo: Date!
        ) {
            exerciseVolumeProgression(
                exerciseId: $exerciseId
                dateFrom: $dateFrom
                dateTo: $dateTo
            ) {
                dataPoints {
                    date
                    totalVolume
                    sessionCount
                }
            }
        }
    """
    
    variables = {
        "exerciseId": str(exercise.id),
        "dateFrom": str(base_date),
        "dateTo": str(base_date + timedelta(days=20)),
    }
    
    response = await graphql_client.post(
        "/graphql",
        json={"query": query, "variables": variables},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()["data"]["exerciseVolumeProgression"]
    
    assert len(data["dataPoints"]) == 3
    
    # Week 1: 2 sessions × 3 sets × 5 reps × 140kg = 4200kg
    assert data["dataPoints"][0]["totalVolume"] == 4200.0
    
    # Week 2: Deload (zero volume)
    assert data["dataPoints"][1]["totalVolume"] == 0.0
    assert data["dataPoints"][1]["sessionCount"] == 0
    
    # Week 3: 2 sessions × 3 sets × 5 reps × 145kg = 4350kg
    assert data["dataPoints"][2]["totalVolume"] == 4350.0
```

---

## Files to Modify/Create

### New Files
- `src/app/application/dtos/insights.py` (update with new DTOs)
- `tests/unit/application/services/test_insight_service_volume.py`
- `tests/integration/test_exercise_volume_progression.py`

### Modified Files
- `src/app/application/services/insight_service.py` (add volume progression method)
- `src/app/infrastructure/repositories/session_repository.py` (add `get_by_date_range`)
- `src/app/domain/repositories/session_repository.py` (update interface)
- `src/app/presentation/graphql/types/insights.py` (add GraphQL types)
- `src/app/presentation/graphql/resolvers/insights.py` (add resolver)
- `src/app/presentation/graphql/schema.py` (register query)

---

## Success Criteria Checklist

- [ ] All unit tests pass (`uv run pytest tests/unit/application/services/test_insight_service_volume.py -v`)
- [ ] All integration tests pass (`uv run pytest tests/integration/test_exercise_volume_progression.py -v`)
- [ ] Full test suite passes (`uv run pytest`)
- [ ] Type checking passes (`uv run mypy src`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] GraphQL schema exports without errors
- [ ] Query executes in <500ms for 1 year of data
- [ ] Volume calculations are accurate (manually verified)
- [ ] Deload weeks show zero volume correctly
- [ ] Incomplete sets are properly excluded
- [ ] Peak and lowest weeks are correctly identified
- [ ] Volume change percentage is accurate
- [ ] Daily vs weekly granularity works correctly
- [ ] Documentation updated (if needed)

---

## Commands Reference

```bash
# Run unit tests only
uv run pytest tests/unit/application/services/test_insight_service_volume.py -v

# Run integration tests only
uv run pytest tests/integration/test_exercise_volume_progression.py -v

# Run all tests with coverage
uv run pytest --cov=app.application.services.insight_service --cov-report=term-missing

# Type checking
uv run mypy src

# Linting
uv run ruff check .

# Format code
uv run ruff format .

# Export GraphQL schema
PYTHONPATH=src uv run python src/export_schema.py > schema.graphql

# Start development server
uv run uvicorn app.main:create_app --factory --reload

# Manual GraphQL testing (with auth header)
curl -X POST http://localhost:8000/graphql \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { exerciseVolumeProgression(exerciseId: \"<uuid>\", dateFrom: \"2026-01-01\", dateTo: \"2026-03-31\") { exerciseName granularity dataPoints { date totalVolume totalSets sessionCount avgIntensity } totalVolumeChangePct avgWeeklyVolume peakWeek { date totalVolume } lowestWeek { date totalVolume } } }"
  }'
```

---

## Implementation Notes

### Volume Calculation Deep Dive

```python
# Set-level volume
set_volume = actual_reps × actual_weight_kg

# Session-level volume (for one exercise)
session_volume = Σ(set_volume for all sets of exercise in session)

# Period-level volume (week or day)
period_volume = Σ(session_volume for all sessions in period)

# Example:
# Session 1: Squat 3x5 @ 100kg = 3 sets × 5 reps × 100kg = 1500kg
# Session 2: Squat 3x5 @ 105kg = 3 sets × 5 reps × 105kg = 1575kg
# Week volume: 1500kg + 1575kg = 3075kg
```

### ISO Week Calculation

```python
from datetime import date, timedelta

def get_week_start(d: date) -> date:
    """
    Get the Monday of the ISO week containing the given date.
    
    ISO 8601: Week starts on Monday (1), ends on Sunday (7).
    """
    weekday = d.isoweekday()  # Mon=1, Sun=7
    days_since_monday = weekday - 1
    return d - timedelta(days=days_since_monday)

# Example:
# date(2026, 1, 8) is Thursday (weekday=4)
# days_since_monday = 4 - 1 = 3
# week_start = 2026-01-08 - 3 days = 2026-01-05 (Monday)
```

### Handling Edge Cases

1. **Incomplete Sets**:
   ```python
   # Skip sets where:
   if (actual_reps is None or 
       actual_weight_kg is None or 
       actual_reps <= 0 or 
       actual_weight_kg < 0):
       continue  # Don't include in volume calculations
   ```

2. **Zero-Volume Periods (Deload)**:
   ```python
   # For weekly granularity, fill missing weeks with zero-volume data points
   # This ensures deload weeks are visible in the progression
   if current_week not in data_map:
       data_points.append(VolumeDataPoint(
           date=current_week_start,
           total_volume=0.0,
           total_sets=0,
           avg_intensity=0.0,
           session_count=0,
       ))
   ```

3. **Volume Change from Zero**:
   ```python
   # If first period has zero volume, can't calculate % change
   if first_volume == 0:
       total_volume_change_pct = None  # Not calculable
   ```

4. **Single Data Point**:
   ```python
   # Need at least 2 data points to calculate change
   if len(data_points) < 2:
       total_volume_change_pct = None
   ```

### Performance Considerations

1. **Date Range Filtering**: Use database-level filtering with indexes on `started_at`
2. **Eager Loading**: Use `selectinload` for session exercises and sets to avoid N+1 queries
3. **Grouping Efficiency**: Use `defaultdict` for O(1) period lookups
4. **Memory**: Limit to 1 year max (52 weeks or 365 days) to prevent excessive memory usage

### GraphQL Query Examples

```graphql
# Basic weekly progression (12 weeks)
query {
  exerciseVolumeProgression(
    exerciseId: "123e4567-e89b-12d3-a456-426614174000"
    dateFrom: "2026-01-01"
    dateTo: "2026-03-31"
  ) {
    exerciseName
    granularity
    dataPoints {
      date
      totalVolume
      totalSets
      avgIntensity
      sessionCount
    }
    totalVolumeChangePct
    avgWeeklyVolume
    peakWeek {
      date
      totalVolume
    }
    lowestWeek {
      date
      totalVolume
    }
  }
}

# Daily progression (2 weeks)
query {
  exerciseVolumeProgression(
    exerciseId: "123e4567-e89b-12d3-a456-426614174000"
    dateFrom: "2026-03-10"
    dateTo: "2026-03-24"
  ) {
    granularity  # Will be "daily"
    dataPoints {
      date
      totalVolume
      sessionCount
    }
  }
}
```

---

## Subagent Assignment Template

When assigning this task to a subagent, use:

```markdown
Please implement Task 07: Exercise Volume Progression for the Workout Tracker API.

**Context**: This is part of Phase 2 (Enhanced Analytics Core). We need to track training volume progression over time to help users identify progressive overload.

**Your responsibilities**:
1. Create DTOs: `VolumeDataPoint` and `ExerciseVolumeProgressionDTO` in `src/app/application/dtos/insights.py`
2. Implement `get_exercise_volume_progression()` in `InsightService`
3. Add `get_by_date_range()` method to `SessionRepository` (interface and implementation)
4. Create GraphQL types and resolver for `exerciseVolumeProgression` query
5. Write comprehensive unit tests (volume calculations, granularity, edge cases)
6. Write integration tests (GraphQL queries, deload weeks)

**Key requirements**:
- Volume formula: `reps × weight` per set, summed for periods
- Use weekly granularity for date ranges >30 days, daily for ≤30 days
- Include zero-volume weeks (deloads) in weekly data
- Skip incomplete sets (missing reps or weight)
- Limit date range to 365 days max
- Calculate: total change %, peak week, lowest week, avg weekly volume

**Definition of Done**:
- All tests pass (unit + integration)
- Type checking passes (mypy)
- Linting passes (ruff)
- Query executes in <500ms for 1 year data
- GraphQL schema exports successfully

Reference: `/home/rc/Dev/repo/workouter/api/docs/enhancement/07-exercise-volume-progression.md`
```

---

## Next Steps

After completing this task:

1. **Verify Volume Calculations**: Manually test with known data to ensure accuracy
2. **Performance Testing**: Load test with 1 year of dense session data
3. **UI Integration**: Coordinate with frontend team for volume chart visualization
4. **Proceed to Task 08**: [Mesocycle Summary Analytics](./08-mesocycle-summary.md)

---

## Related Documentation

- [Task 05: Performance Trends](./05-performance-trends.md)
- [Task 06: Exercise PRs](./06-exercise-prs.md)
- [Task 08: Mesocycle Summary](./08-mesocycle-summary.md)
- [Clean Architecture Guidelines](../architecture/clean-architecture.md)
- [GraphQL Conventions](../api/graphql-conventions.md)

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-25  
**Author**: AI Assistant
