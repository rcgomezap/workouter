from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.application.services.calendar_service import CalendarService
from workouter_cli.domain.entities.calendar import CalendarDay


def _calendar_day() -> CalendarDay:
    return CalendarDay(
        date="2026-01-01",
        planned_session=None,
        session_id=None,
        is_completed=False,
        is_rest_day=False,
    )


@pytest.mark.asyncio
async def test_calendar_service_day_and_range_delegate(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.day = AsyncMock(return_value=_calendar_day())
    repository.range = AsyncMock(return_value=[_calendar_day()])
    service = CalendarService(calendar_repository=repository)

    day = await service.day("2026-01-01")
    days = await service.range("2026-01-01", "2026-01-07")

    assert day.date == "2026-01-01"
    assert len(days) == 1
    repository.day.assert_awaited_once_with("2026-01-01")
    repository.range.assert_awaited_once_with("2026-01-01", "2026-01-07")
