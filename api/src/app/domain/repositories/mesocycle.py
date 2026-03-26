from collections.abc import Sequence
from datetime import date
from typing import Protocol
from uuid import UUID

from app.domain.entities.mesocycle import Mesocycle, MesocycleWeek, PlannedSession
from app.domain.enums import MesocycleStatus
from app.domain.repositories.base import BaseRepository


class MesocycleRepository(BaseRepository[Mesocycle], Protocol):
    async def list_by_status(
        self, status: MesocycleStatus, offset: int = 0, limit: int = 20
    ) -> Sequence[Mesocycle]: ...

    async def count_by_status(self, status: MesocycleStatus) -> int: ...

    async def count_total(self) -> int: ...

    async def get_week_by_id(self, week_id: UUID) -> MesocycleWeek | None: ...

    async def get_planned_session_by_id(self, ps_id: UUID) -> PlannedSession | None: ...

    async def get_planned_sessions_by_date_range(
        self, start_date: date, end_date: date
    ) -> Sequence[PlannedSession]: ...
