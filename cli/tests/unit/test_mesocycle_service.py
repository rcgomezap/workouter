from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock

import pytest

from workouter_cli.application.dto.mesocycle import (
    AddMesocycleWeekInputDTO,
    AddPlannedSessionInputDTO,
    CreateMesocycleInputDTO,
    UpdateMesocycleInputDTO,
    UpdateMesocycleWeekInputDTO,
    UpdatePlannedSessionInputDTO,
)
from workouter_cli.application.services.mesocycle_service import MesocycleService
from workouter_cli.domain.entities.mesocycle import (
    Mesocycle,
    MesocyclePlannedSession,
    MesocycleWeek,
)


def _mesocycle() -> Mesocycle:
    return Mesocycle(
        id="11111111-1111-1111-1111-111111111111",
        name="Hypertrophy Block",
        description="Upper focus",
        start_date="2026-01-01",
        end_date=None,
        status="PLANNED",
        weeks=(),
    )


def _week() -> MesocycleWeek:
    return MesocycleWeek(
        id="22222222-2222-2222-2222-222222222222",
        week_number=1,
        week_type="TRAINING",
        start_date="2026-01-01",
        end_date="2026-01-07",
        planned_sessions=(),
    )


def _planned_session() -> MesocyclePlannedSession:
    return MesocyclePlannedSession(
        id="33333333-3333-3333-3333-333333333333",
        routine_id="44444444-4444-4444-4444-444444444444",
        routine_name="Push A",
        day_of_week=1,
        date="2026-01-01",
        notes="Heavy compounds",
    )


@pytest.mark.asyncio
async def test_mesocycle_service_crud_delegates(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.list = AsyncMock(
        return_value=([_mesocycle()], {"total": 1, "page": 1, "pageSize": 20, "totalPages": 1})
    )
    repository.get = AsyncMock(return_value=_mesocycle())
    repository.create = AsyncMock(return_value=_mesocycle())
    repository.update = AsyncMock(return_value=_mesocycle())
    repository.delete = AsyncMock(return_value=True)
    repository.add_week = AsyncMock(return_value=_week())
    repository.update_week = AsyncMock(return_value=_week())
    repository.remove_week = AsyncMock(return_value=True)
    repository.add_session = AsyncMock(return_value=_planned_session())
    repository.update_session = AsyncMock(return_value=_planned_session())
    repository.remove_session = AsyncMock(return_value=True)

    service = MesocycleService(mesocycle_repository=repository)

    items, pagination = await service.list(page=1, page_size=20, status="PLANNED")
    fetched = await service.get("11111111-1111-1111-1111-111111111111")
    created = await service.create(
        CreateMesocycleInputDTO(
            name="Hypertrophy Block",
            start_date=date(2026, 1, 1),
        )
    )
    updated = await service.update(
        "11111111-1111-1111-1111-111111111111",
        UpdateMesocycleInputDTO(status="ACTIVE"),
    )
    deleted = await service.delete("11111111-1111-1111-1111-111111111111")
    added_week = await service.add_week(
        "11111111-1111-1111-1111-111111111111",
        AddMesocycleWeekInputDTO(
            weekNumber=1,
            weekType="TRAINING",
            startDate=date(2026, 1, 1),
            endDate=date(2026, 1, 7),
        ),
    )
    updated_week = await service.update_week(
        "22222222-2222-2222-2222-222222222222",
        UpdateMesocycleWeekInputDTO(weekType="DELOAD"),
    )
    removed_week = await service.remove_week("22222222-2222-2222-2222-222222222222")
    added_session = await service.add_session(
        "22222222-2222-2222-2222-222222222222",
        AddPlannedSessionInputDTO(
            routineId="44444444-4444-4444-4444-444444444444",
            dayOfWeek=1,
            date=date(2026, 1, 1),
        ),
    )
    updated_session = await service.update_session(
        "33333333-3333-3333-3333-333333333333",
        UpdatePlannedSessionInputDTO(notes="Updated"),
    )
    removed_session = await service.remove_session("33333333-3333-3333-3333-333333333333")

    assert len(items) == 1
    assert pagination["total"] == 1
    assert fetched.name == "Hypertrophy Block"
    assert created.status == "PLANNED"
    assert updated.id == "11111111-1111-1111-1111-111111111111"
    assert deleted is True
    assert added_week.week_number == 1
    assert updated_week.week_type == "TRAINING"
    assert removed_week is True
    assert added_session.day_of_week == 1
    assert updated_session.id == "33333333-3333-3333-3333-333333333333"
    assert removed_session is True

    repository.list.assert_awaited_once_with(page=1, page_size=20, status="PLANNED")
    repository.get.assert_awaited_once_with("11111111-1111-1111-1111-111111111111")
    repository.create.assert_awaited_once_with(
        {"name": "Hypertrophy Block", "startDate": "2026-01-01"}
    )
    repository.update.assert_awaited_once_with(
        "11111111-1111-1111-1111-111111111111",
        {"status": "ACTIVE"},
    )
    repository.delete.assert_awaited_once_with("11111111-1111-1111-1111-111111111111")
    repository.add_week.assert_awaited_once_with(
        "11111111-1111-1111-1111-111111111111",
        {
            "weekNumber": 1,
            "weekType": "TRAINING",
            "startDate": "2026-01-01",
            "endDate": "2026-01-07",
        },
    )
    repository.update_week.assert_awaited_once_with(
        "22222222-2222-2222-2222-222222222222",
        {"weekType": "DELOAD"},
    )
    repository.remove_week.assert_awaited_once_with("22222222-2222-2222-2222-222222222222")
    repository.add_session.assert_awaited_once_with(
        "22222222-2222-2222-2222-222222222222",
        {
            "routineId": "44444444-4444-4444-4444-444444444444",
            "dayOfWeek": 1,
            "date": "2026-01-01",
        },
    )
    repository.update_session.assert_awaited_once_with(
        "33333333-3333-3333-3333-333333333333",
        {"notes": "Updated"},
    )
    repository.remove_session.assert_awaited_once_with("33333333-3333-3333-3333-333333333333")
