from datetime import date
from typing import Protocol, Sequence
from uuid import UUID
from app.domain.entities.session import Session, SessionSet
from app.domain.enums import SessionStatus
from app.domain.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session], Protocol):
    async def list_by_filters(
        self,
        status: SessionStatus | None = None,
        mesocycle_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[Session]: ...

    async def count_by_filters(
        self,
        status: SessionStatus | None = None,
        mesocycle_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int: ...

    async def get_by_date_range(self, start_date: date, end_date: date) -> Sequence[Session]: ...

    async def get_set_by_id(self, set_id: UUID) -> SessionSet | None: ...

    async def update_set(self, session_set: SessionSet) -> SessionSet: ...
