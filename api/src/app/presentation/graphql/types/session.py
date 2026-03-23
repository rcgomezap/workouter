from uuid import UUID
from datetime import datetime
from decimal import Decimal
import strawberry
from app.presentation.graphql.types.enums import SessionStatus, SetType
from app.presentation.graphql.types.exercise import Exercise

@strawberry.type
class SessionSet:
    id: UUID
    set_number: int
    set_type: SetType
    target_reps: int | None
    target_rir: int | None
    target_weight_kg: Decimal | None
    actual_reps: int | None
    actual_rir: int | None
    actual_weight_kg: Decimal | None
    weight_reduction_pct: Decimal | None
    rest_seconds: int | None
    performed_at: datetime | None

@strawberry.type
class SessionExercise:
    id: UUID
    exercise: Exercise
    order: int
    superset_group: int | None
    rest_seconds: int | None
    notes: str | None
    sets: list[SessionSet]

@strawberry.type
class Session:
    id: UUID
    planned_session_id: UUID | None
    mesocycle_id: UUID | None
    routine_id: UUID | None
    status: SessionStatus
    started_at: datetime | None
    completed_at: datetime | None
    notes: str | None
    exercises: list[SessionExercise]

@strawberry.type
class PaginatedSessions:
    items: list[Session]
    total: int
    page: int
    page_size: int
    total_pages: int
