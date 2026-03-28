from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.application.services.bodyweight_service import BodyweightService
from workouter_cli.domain.entities.bodyweight import BodyweightLog


def _bodyweight_log() -> BodyweightLog:
    return BodyweightLog(
        id="11111111-1111-1111-1111-111111111111",
        weight_kg=80.5,
        recorded_at="2026-01-01T08:00:00Z",
        notes="Morning",
        created_at="2026-01-01T08:00:00Z",
    )


@pytest.mark.asyncio
async def test_bodyweight_service_delegates(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.list = AsyncMock(
        return_value=([_bodyweight_log()], {"total": 1, "page": 1, "pageSize": 20, "totalPages": 1})
    )
    repository.log = AsyncMock(return_value=_bodyweight_log())
    repository.update = AsyncMock(return_value=_bodyweight_log())
    repository.delete = AsyncMock(return_value=True)

    service = BodyweightService(bodyweight_repository=repository)

    items, pagination = await service.list(page=1, page_size=20)
    logged = await service.log({"weightKg": 80.5})
    updated = await service.update("11111111-1111-1111-1111-111111111111", {"notes": "Updated"})
    deleted = await service.delete("11111111-1111-1111-1111-111111111111")

    assert len(items) == 1
    assert pagination["total"] == 1
    assert logged.weight_kg == 80.5
    assert updated.id == "11111111-1111-1111-1111-111111111111"
    assert deleted is True

    repository.list.assert_awaited_once_with(page=1, page_size=20, date_from=None, date_to=None)
    repository.log.assert_awaited_once_with({"weightKg": 80.5})
    repository.update.assert_awaited_once_with(
        "11111111-1111-1111-1111-111111111111", {"notes": "Updated"}
    )
    repository.delete.assert_awaited_once_with("11111111-1111-1111-1111-111111111111")
