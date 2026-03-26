from collections.abc import Sequence
from datetime import date
from typing import Protocol

from app.domain.entities.bodyweight import BodyweightLog
from app.domain.repositories.base import BaseRepository


class BodyweightRepository(BaseRepository[BodyweightLog], Protocol):
    async def list_by_date_range(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[BodyweightLog]:
        ...

    async def count_by_date_range(
        self, date_from: date | None = None, date_to: date | None = None
    ) -> int:
        ...
