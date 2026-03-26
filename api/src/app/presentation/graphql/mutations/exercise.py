from uuid import UUID

import strawberry
from strawberry.types import Info

from app.application.dto.exercise import CreateExerciseInput as CreateExerciseDTO
from app.application.dto.exercise import MuscleGroupAssignmentInput as MuscleGroupAssignmentDTO
from app.application.dto.exercise import UpdateExerciseInput as UpdateExerciseDTO
from app.presentation.graphql.context import Context
from app.presentation.graphql.inputs.exercise import (
    CreateExerciseInput,
    MuscleGroupAssignmentInput,
    UpdateExerciseInput,
)
from app.presentation.graphql.types.exercise import Exercise


@strawberry.type
class ExerciseMutation:
    @strawberry.mutation
    async def create_exercise(
        self, 
        info: Info[Context, None], 
        input: CreateExerciseInput
    ) -> Exercise:
        dto = CreateExerciseDTO(
            name=input.name,
            description=input.description,
            equipment=input.equipment
        )
        e = await info.context.exercise_service.create_exercise(dto)
        return Exercise(
            id=e.id,
            name=e.name,
            description=e.description,
            equipment=e.equipment,
            muscle_groups=[]
        )

    @strawberry.mutation
    async def update_exercise(
        self, 
        info: Info[Context, None], 
        id: UUID, 
        input: UpdateExerciseInput
    ) -> Exercise:
        dto = UpdateExerciseDTO(
            name=input.name,
            description=input.description,
            equipment=input.equipment
        )
        e = await info.context.exercise_service.update_exercise(id, dto)
        return Exercise(
            id=e.id,
            name=e.name,
            description=e.description,
            equipment=e.equipment,
            muscle_groups=[]
        )

    @strawberry.mutation
    async def delete_exercise(self, info: Info[Context, None], id: UUID) -> bool:
        return await info.context.exercise_service.delete_exercise(id)

    @strawberry.mutation
    async def assign_muscle_groups(
        self, 
        info: Info[Context, None], 
        exercise_id: UUID, 
        muscle_group_ids: list[MuscleGroupAssignmentInput]
    ) -> Exercise:
        dtos = [MuscleGroupAssignmentDTO(
            muscle_group_id=m.muscle_group_id,
            role=m.role
        ) for m in muscle_group_ids]
        e = await info.context.exercise_service.assign_muscle_groups(exercise_id, dtos)
        return Exercise(
            id=e.id,
            name=e.name,
            description=e.description,
            equipment=e.equipment,
            muscle_groups=[]
        )
