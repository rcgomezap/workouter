from uuid import UUID
import strawberry
from app.presentation.graphql.types.enums import MuscleRole

@strawberry.type
class MuscleGroup:
    id: UUID
    name: str

@strawberry.type
class ExerciseMuscleGroup:
    muscle_group: MuscleGroup
    role: MuscleRole

@strawberry.type
class Exercise:
    id: UUID
    name: str
    description: str | None
    equipment: str | None
    muscle_groups: list[ExerciseMuscleGroup]

@strawberry.type
class PaginatedExercises:
    items: list[Exercise]
    total: int
    page: int
    page_size: int
    total_pages: int
