from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


class MuscleGroup(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    name: str
