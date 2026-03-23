from typing import Protocol, Sequence
from app.domain.entities.muscle_group import MuscleGroup
from app.domain.repositories.base import BaseRepository


class MuscleGroupRepository(BaseRepository[MuscleGroup], Protocol):
    async def get_by_name(self, name: str) -> MuscleGroup | None:
        ...

    async def list_all(self) -> Sequence[MuscleGroup]:
        ...
