from uuid import UUID
from pydantic import BaseModel, Field
from app.domain.enums import MuscleRole
from app.application.dto.pagination import PaginatedResult

class MuscleGroupDTO(BaseModel):
    id: UUID
    name: str

class ExerciseMuscleGroupDTO(BaseModel):
    muscle_group: MuscleGroupDTO
    role: MuscleRole

class ExerciseDTO(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    equipment: str | None = None
    muscle_groups: list[ExerciseMuscleGroupDTO] = []

class CreateExerciseInput(BaseModel):
    name: str
    description: str | None = None
    equipment: str | None = None

class UpdateExerciseInput(BaseModel):
    name: str | None = None
    description: str | None = None
    equipment: str | None = None

class MuscleGroupAssignmentInput(BaseModel):
    muscle_group_id: UUID
    role: MuscleRole

class PaginatedExercises(PaginatedResult[ExerciseDTO]):
    pass
