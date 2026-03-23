from typing import Protocol, Sequence
from app.domain.entities.mesocycle import Mesocycle
from app.domain.enums import MesocycleStatus
from app.domain.repositories.base import BaseRepository


class MesocycleRepository(BaseRepository[Mesocycle], Protocol):
    async def list_by_status(
        self, status: MesocycleStatus, offset: int = 0, limit: int = 20
    ) -> Sequence[Mesocycle]:
        ...

    async def count_by_status(self, status: MesocycleStatus) -> int:
        ...

    async def count_total(self) -> int:
        ...
