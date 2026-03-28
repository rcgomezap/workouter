"""Calendar application service."""

from __future__ import annotations

from workouter_cli.domain.entities.calendar import CalendarDay
from workouter_cli.domain.repositories.calendar import CalendarRepository


class CalendarService:
    """Calendar use-cases orchestration."""

    def __init__(self, calendar_repository: CalendarRepository) -> None:
        self.calendar_repository = calendar_repository

    async def day(self, date: str) -> CalendarDay:
        return await self.calendar_repository.day(date)
