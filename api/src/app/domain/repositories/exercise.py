from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.domain.entities.exercise import Exercise
from app.domain.repositories.base import BaseRepository


class ExerciseRepository(BaseRepository[Exercise], Protocol):
    async def list_by_muscle_group(
        self, muscle_group_id: UUID, offset: int = 0, limit: int = 20
    ) -> Sequence[Exercise]:
        ...

    async def count_by_muscle_group(self, muscle_group_id: UUID) -> int:
        ...

    async def count_total(self) -> int:
        ...
