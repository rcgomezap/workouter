import strawberry
from uuid import UUID
from strawberry.types import Info
from app.presentation.graphql.context import Context
from app.presentation.graphql.types.exercise import Exercise, PaginatedExercises, MuscleGroup
from app.presentation.graphql.inputs.pagination import PaginationInput
from app.application.dto.pagination import PaginationInput as PaginationDTO

@strawberry.type
class ExerciseQuery:
    @strawberry.field
    async def exercises(
        self, 
        info: Info[Context, None], 
        pagination: PaginationInput | None = None, 
        muscle_group_id: UUID | None = None
    ) -> PaginatedExercises:
        p_dto = PaginationDTO(
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else 20
        )
        result = await info.context.exercise_service.list_exercises(p_dto, muscle_group_id)
        return PaginatedExercises(
            items=[Exercise(
                id=e.id,
                name=e.name,
                description=e.description,
                equipment=e.equipment,
                muscle_groups=[] # Simplified mapping for now, should map properly
            ) for e in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages
        )

    @strawberry.field
    async def exercise(self, info: Info[Context, None], id: UUID) -> Exercise:
        e = await info.context.exercise_service.get_exercise(id)
        return Exercise(
            id=e.id,
            name=e.name,
            description=e.description,
            equipment=e.equipment,
            muscle_groups=[] # Simplified
        )

    @strawberry.field
    async def muscle_groups(self, info: Info[Context, None]) -> list[MuscleGroup]:
        mgs = await info.context.muscle_group_service.list_muscle_groups()
        return [MuscleGroup(id=mg.id, name=mg.name) for mg in mgs]
