"""Calendar repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.calendar import CalendarDay


class CalendarRepository(Protocol):
    """Persistence contract for calendar lookups."""

    async def day(self, date: str) -> CalendarDay:
        """Get a single calendar day by date."""
        ...
