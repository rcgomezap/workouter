from decimal import Decimal
from uuid import UUID

from app.domain.entities.common import BaseEntity, TimestampedEntity
from app.domain.entities.exercise import Exercise
from app.domain.enums import SetType


class RoutineSet(BaseEntity):
    routine_exercise_id: UUID | None = None
    set_number: int
    set_type: SetType = SetType.STANDARD
    target_reps_min: int | None = None
    target_reps_max: int | None = None
    target_rir: int | None = None
    target_weight_kg: Decimal | None = None
    weight_reduction_pct: Decimal | None = None
    rest_seconds: int | None = None


class RoutineExercise(BaseEntity):
    routine_id: UUID | None = None
    exercise: Exercise
    order: int
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None
    sets: list[RoutineSet] = []


class Routine(TimestampedEntity):
    name: str
    description: str | None = None
    exercises: list[RoutineExercise] = []
