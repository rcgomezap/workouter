from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.infrastructure.graphql.queries.calendar import CALENDAR_DAY, CALENDAR_RANGE
from workouter_cli.infrastructure.repositories.calendar import GraphQLCalendarRepository


def _calendar_day_payload() -> dict[str, object]:
    return {
        "date": "2026-01-01",
        "plannedSession": {
            "id": "11111111-1111-1111-1111-111111111111",
            "routine": {
                "id": "22222222-2222-2222-2222-222222222222",
                "name": "Push A",
            },
            "dayOfWeek": 4,
            "date": "2026-01-01",
            "notes": None,
        },
        "session": None,
        "isCompleted": False,
        "isRestDay": False,
    }


@pytest.mark.asyncio
async def test_repository_day_maps_calendar_day() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"calendarDay": _calendar_day_payload()})

    repository = GraphQLCalendarRepository(client=client)
    day = await repository.day("2026-01-01")

    assert day.date == "2026-01-01"
    assert day.is_rest_day is False
    client.execute.assert_awaited_once_with(CALENDAR_DAY, {"date": "2026-01-01"})


@pytest.mark.asyncio
async def test_repository_range_maps_calendar_days() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"calendarRange": [_calendar_day_payload()]})

    repository = GraphQLCalendarRepository(client=client)
    days = await repository.range("2026-01-01", "2026-01-07")

    assert len(days) == 1
    assert days[0].planned_session is not None
    client.execute.assert_awaited_once_with(
        CALENDAR_RANGE,
        {"startDate": "2026-01-01", "endDate": "2026-01-07"},
    )
