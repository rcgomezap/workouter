from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import Field
from app.domain.entities.common import TimestampedEntity, BaseEntity
from app.domain.entities.exercise import Exercise
from app.domain.enums import SessionStatus, SetType


class SessionSet(BaseEntity):
    set_number: int
    set_type: SetType
    target_reps: int | None = None
    target_rir: int | None = None
    target_weight_kg: Decimal | None = None
    actual_reps: int | None = None
    actual_rir: int | None = None
    actual_weight_kg: Decimal | None = None
    weight_reduction_pct: Decimal | None = None
    rest_seconds: int | None = None
    performed_at: datetime | None = None


class SessionExercise(BaseEntity):
    exercise: Exercise
    order: int
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None
    sets: list[SessionSet] = Field(default_factory=list)


class Session(TimestampedEntity):
    planned_session_id: UUID | None = None
    mesocycle_id: UUID | None = None
    routine_id: UUID | None = None
    status: SessionStatus = SessionStatus.PLANNED
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None
    exercises: list[SessionExercise] = Field(default_factory=list)
