from typing import Protocol
from app.domain.entities.routine import Routine
from app.domain.repositories.base import BaseRepository


class RoutineRepository(BaseRepository[Routine], Protocol):
    async def count_total(self) -> int:
        ...
