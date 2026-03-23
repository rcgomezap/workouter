from uuid import UUID
from datetime import datetime
from decimal import Decimal
import strawberry
from app.presentation.graphql.types.enums import SessionStatus, SetType


@strawberry.input
class CreateSessionInput:
    planned_session_id: UUID | None = None
    mesocycle_id: UUID | None = None
    routine_id: UUID | None = None
    notes: str | None = None


@strawberry.input
class UpdateSessionInput:
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: SessionStatus | None = None
    notes: str | None = None


@strawberry.input
class AddSessionExerciseInput:
    exercise_id: UUID
    order: int
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None


@strawberry.input
class UpdateSessionExerciseInput:
    order: int | None = None
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None


@strawberry.input
class AddSessionSetInput:
    set_number: int
    set_type: SetType
    target_reps: int | None = None
    target_rir: int | None = None
    target_weight_kg: Decimal | None = None
    weight_reduction_pct: Decimal | None = None
    rest_seconds: int | None = None


@strawberry.input
class UpdateSessionSetInput:
    set_number: int | None = None
    set_type: SetType | None = None
    target_reps: int | None = None
    target_rir: int | None = None
    target_weight_kg: Decimal | None = None
    weight_reduction_pct: Decimal | None = None
    rest_seconds: int | None = None


@strawberry.input
class LogSetResultInput:
    actual_reps: int
    actual_rir: int | None = None
    actual_weight_kg: Decimal
    performed_at: datetime | None = None
