from decimal import Decimal
from uuid import UUID

import strawberry

from app.presentation.graphql.types.enums import SetType
from app.presentation.graphql.types.exercise import Exercise


@strawberry.type
class RoutineSet:
    id: UUID
    set_number: int
    set_type: SetType
    target_reps_min: int | None
    target_reps_max: int | None
    target_rir: int | None
    target_weight_kg: Decimal | None
    weight_reduction_pct: Decimal | None
    rest_seconds: int | None

@strawberry.type
class RoutineExercise:
    id: UUID
    exercise: Exercise
    order: int
    superset_group: int | None
    rest_seconds: int | None
    notes: str | None
    sets: list[RoutineSet]

@strawberry.type
class Routine:
    id: UUID
    name: str
    description: str | None
    exercises: list[RoutineExercise]

@strawberry.type
class PaginatedRoutines:
    items: list[Routine]
    total: int
    page: int
    page_size: int
    total_pages: int
