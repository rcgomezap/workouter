from uuid import UUID
import strawberry
from app.presentation.graphql.types.enums import MuscleRole

@strawberry.input
class CreateExerciseInput:
    name: str
    description: str | None = None
    equipment: str | None = None

@strawberry.input
class UpdateExerciseInput:
    name: str | None = None
    description: str | None = None
    equipment: str | None = None

@strawberry.input
class MuscleGroupAssignmentInput:
    muscle_group_id: UUID
    role: MuscleRole
