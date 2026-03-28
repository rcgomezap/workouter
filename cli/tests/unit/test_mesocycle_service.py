from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock

import pytest

from workouter_cli.application.dto.mesocycle import CreateMesocycleInputDTO, UpdateMesocycleInputDTO
from workouter_cli.application.services.mesocycle_service import MesocycleService
from workouter_cli.domain.entities.mesocycle import Mesocycle


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

    assert len(items) == 1
    assert pagination["total"] == 1
    assert fetched.name == "Hypertrophy Block"
    assert created.status == "PLANNED"
    assert updated.id == "11111111-1111-1111-1111-111111111111"
    assert deleted is True

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
