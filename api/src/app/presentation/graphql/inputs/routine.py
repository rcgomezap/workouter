from uuid import UUID
from decimal import Decimal
import strawberry
from app.presentation.graphql.types.enums import SetType

@strawberry.input
class CreateRoutineInput:
    name: str
    description: str | None = None

@strawberry.input
class UpdateRoutineInput:
    name: str | None = None
    description: str | None = None

@strawberry.input
class AddRoutineExerciseInput:
    exercise_id: UUID
    order: int
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None

@strawberry.input
class UpdateRoutineExerciseInput:
    order: int | None = None
    superset_group: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None

@strawberry.input
class AddRoutineSetInput:
    set_number: int
    set_type: SetType = SetType.STANDARD
    target_reps_min: int | None = None
    target_reps_max: int | None = None
    target_rir: int | None = None
    target_weight_kg: Decimal | None = None
    weight_reduction_pct: Decimal | None = None
    rest_seconds: int | None = None

@strawberry.input
class UpdateRoutineSetInput:
    set_number: int | None = None
    set_type: SetType | None = None
    target_reps_min: int | None = None
    target_reps_max: int | None = None
    target_rir: int | None = None
    target_weight_kg: Decimal | None = None
    weight_reduction_pct: Decimal | None = None
    rest_seconds: int | None = None
