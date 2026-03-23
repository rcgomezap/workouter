from pydantic import BaseModel, ConfigDict
from app.domain.entities.common import TimestampedEntity
from app.domain.entities.muscle_group import MuscleGroup
from app.domain.enums import MuscleRole


class ExerciseMuscleGroup(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    muscle_group: MuscleGroup
    role: MuscleRole


class Exercise(TimestampedEntity):
    name: str
    description: str | None = None
    equipment: str | None = None
    muscle_groups: list[ExerciseMuscleGroup] = []
