from typing import Any
from uuid import UUID

import strawberry
from strawberry.types import Info

from app.application.dto.pagination import PaginationInput as PaginationDTO
from app.presentation.graphql.context import Context
from app.presentation.graphql.inputs.pagination import PaginationInput
from app.presentation.graphql.types.exercise import Exercise, ExerciseMuscleGroup, MuscleGroup
from app.presentation.graphql.types.routine import (
    PaginatedRoutines,
    Routine,
    RoutineExercise,
    RoutineSet,
)


def map_routine_set(s: Any) -> RoutineSet:
    return RoutineSet(
        id=s.id,
        set_number=s.set_number,
        set_type=s.set_type,
        target_reps_min=s.target_reps_min,
        target_reps_max=s.target_reps_max,
        target_rir=s.target_rir,
        target_weight_kg=s.target_weight_kg,
        weight_reduction_pct=s.weight_reduction_pct,
        rest_seconds=s.rest_seconds,
    )


def map_exercise(e: Any) -> Exercise:
    muscle_groups = e.muscle_groups if e.muscle_groups is not None else []
    return Exercise(
        id=e.id,
        name=e.name,
        description=e.description,
        equipment=e.equipment,
        muscle_groups=[
            ExerciseMuscleGroup(
                muscle_group=MuscleGroup(id=mg.muscle_group.id, name=mg.muscle_group.name),
                role=mg.role,
            )
            for mg in muscle_groups
        ],
    )


def map_routine_exercise(re: Any) -> RoutineExercise:
    return RoutineExercise(
        id=re.id,
        exercise=map_exercise(re.exercise),
        order=re.order,
        superset_group=re.superset_group,
        rest_seconds=re.rest_seconds,
        notes=re.notes,
        sets=[map_routine_set(s) for s in re.sets],
    )


def map_routine(r: Any) -> Routine:
    return Routine(
        id=r.id,
        name=r.name,
        description=r.description,
        exercises=[map_routine_exercise(re) for re in r.exercises],
    )


@strawberry.type
class RoutineQuery:
    @strawberry.field
    async def routines(
        self, info: Info[Context, None], pagination: PaginationInput | None = None
    ) -> PaginatedRoutines:
        p_dto = PaginationDTO(
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else 20,
        )
        result = await info.context.routine_service.list_routines(p_dto)
        return PaginatedRoutines(
            items=[map_routine(r) for r in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
        )

    @strawberry.field
    async def routine(self, info: Info[Context, None], id: UUID) -> Routine:
        r = await info.context.routine_service.get_routine(id)
        return map_routine(r)
