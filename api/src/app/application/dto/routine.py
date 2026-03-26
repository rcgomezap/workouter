from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.application.dto.exercise import ExerciseDTO
from app.application.dto.pagination import PaginatedResult
from app.domain.enums import SetType


class RoutineSetDTO(BaseModel):
    id: UUID
    set_number: int
    set_type: SetType
    target_reps_min: int | None = None
    target_reps_max: int | None = None
    target_rir: int | None = None
    target_weight_kg: Decimal | None = None
    weight_reduction_pct: Decimal | None = None
    rest_seconds: int | None = None


class RoutineExerciseDTO(BaseModel):
    id: UUID
    exercise: ExerciseDTO
    order: int
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None
    sets: list[RoutineSetDTO]


class RoutineDTO(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    exercises: list[RoutineExerciseDTO]


class CreateRoutineInput(BaseModel):
    name: str
    description: str | None = None


class UpdateRoutineInput(BaseModel):
    name: str | None = None
    description: str | None = None


class AddRoutineExerciseInput(BaseModel):
    exercise_id: UUID
    order: int
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None


class UpdateRoutineExerciseInput(BaseModel):
    order: int | None = None
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None


class AddRoutineSetInput(BaseModel):
    set_number: int
    set_type: SetType = SetType.STANDARD
    target_reps_min: int | None = None
    target_reps_max: int | None = None
    target_rir: int | None = None
    target_weight_kg: Decimal | None = None
    weight_reduction_pct: Decimal | None = None
    rest_seconds: int | None = None


class UpdateRoutineSetInput(BaseModel):
    set_number: int | None = None
    set_type: SetType | None = None
    target_reps_min: int | None = None
    target_reps_max: int | None = None
    target_rir: int | None = None
    target_weight_kg: Decimal | None = None
    weight_reduction_pct: Decimal | None = None
    rest_seconds: int | None = None


class PaginatedRoutines(PaginatedResult[RoutineDTO]):
    pass
