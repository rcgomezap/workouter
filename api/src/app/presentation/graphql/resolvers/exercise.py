from typing import Any
from uuid import UUID

import strawberry
from strawberry.types import Info

from app.application.dto.pagination import PaginationInput as PaginationDTO
from app.presentation.graphql.context import Context
from app.presentation.graphql.inputs.pagination import PaginationInput
from app.presentation.graphql.types.exercise import (
    Exercise,
    ExerciseMuscleGroup,
    MuscleGroup,
    PaginatedExercises,
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


@strawberry.type
class ExerciseQuery:
    @strawberry.field
    async def exercises(
        self,
        info: Info[Context, None],
        pagination: PaginationInput | None = None,
        muscle_group_id: UUID | None = None,
    ) -> PaginatedExercises:
        p_dto = PaginationDTO(
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else 20,
        )
        result = await info.context.exercise_service.list_exercises(p_dto, muscle_group_id)
        return PaginatedExercises(
            items=[map_exercise(e) for e in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
        )

    @strawberry.field
    async def exercise(self, info: Info[Context, None], id: UUID) -> Exercise:
        e = await info.context.exercise_service.get_exercise(id)
        return map_exercise(e)

    @strawberry.field
    async def muscle_groups(self, info: Info[Context, None]) -> list[MuscleGroup]:
        mgs = await info.context.muscle_group_service.get_muscle_groups()
        return [MuscleGroup(id=mg.id, name=mg.name) for mg in mgs]
