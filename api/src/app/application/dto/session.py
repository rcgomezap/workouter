from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.domain.enums import SessionStatus, SetType
from app.application.dto.exercise import ExerciseDTO
from app.application.dto.pagination import PaginatedResult


class SessionSetDTO(BaseModel):
    id: UUID
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


class SessionExerciseDTO(BaseModel):
    id: UUID
    exercise: ExerciseDTO
    order: int
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None
    sets: list[SessionSetDTO]


class SessionDTO(BaseModel):
    id: UUID
    planned_session_id: UUID | None = None
    mesocycle_id: UUID | None = None
    routine_id: UUID | None = None
    status: SessionStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None
    exercises: list[SessionExerciseDTO]


class CreateSessionInput(BaseModel):
    planned_session_id: UUID | None = None
    mesocycle_id: UUID | None = None
    routine_id: UUID | None = None
    notes: str | None = None


class UpdateSessionInput(BaseModel):
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: SessionStatus | None = None
    notes: str | None = None


class AddSessionExerciseInput(BaseModel):
    exercise_id: UUID
    order: int
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None


class UpdateSessionExerciseInput(BaseModel):
    order: int | None = None
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None


class AddSessionSetInput(BaseModel):
    set_number: int
    set_type: SetType
    target_reps: int | None = None
    target_rir: int | None = None
    target_weight_kg: Decimal | None = None
    weight_reduction_pct: Decimal | None = None
    rest_seconds: int | None = None


class UpdateSessionSetInput(BaseModel):
    set_number: int | None = None
    set_type: SetType | None = None
    target_reps: int | None = None
    target_rir: int | None = None
    target_weight_kg: Decimal | None = None
    weight_reduction_pct: Decimal | None = None
    rest_seconds: int | None = None


class LogSetResultInput(BaseModel):
    actual_reps: int
    actual_rir: int | None = None
    actual_weight_kg: Decimal
    performed_at: datetime | None = None


class PaginatedSessions(PaginatedResult[SessionDTO]):
    pass
