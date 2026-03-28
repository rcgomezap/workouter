from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.application.services.session_service import SessionService
from workouter_cli.domain.entities.session import Session


def _session(status: str) -> Session:
    return Session(
        id="11111111-1111-1111-1111-111111111111",
        planned_session_id=None,
        mesocycle_id=None,
        routine_id="33333333-3333-3333-3333-333333333333",
        status=status,
        started_at="2026-01-01T10:00:00Z",
        completed_at=None,
        notes=None,
        exercises=(),
    )


@pytest.mark.asyncio
async def test_session_service_start_delegates_to_repository(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.start = AsyncMock(return_value=_session("IN_PROGRESS"))
    service = SessionService(session_repository=repository)

    result = await service.start("11111111-1111-1111-1111-111111111111")

    assert result.status == "IN_PROGRESS"
    repository.start.assert_awaited_once_with("11111111-1111-1111-1111-111111111111")


@pytest.mark.asyncio
async def test_session_service_complete_delegates_to_repository(mocker) -> None:  # type: ignore[no-untyped-def]
    completed = _session("COMPLETED")
    repository = mocker.Mock()
    repository.complete = AsyncMock(return_value=completed)
    service = SessionService(session_repository=repository)

    result = await service.complete("11111111-1111-1111-1111-111111111111")

    assert result.status == "COMPLETED"
    repository.complete.assert_awaited_once_with("11111111-1111-1111-1111-111111111111")


@pytest.mark.asyncio
async def test_session_service_update_delegates_to_repository(mocker) -> None:  # type: ignore[no-untyped-def]
    updated = _session("IN_PROGRESS")
    repository = mocker.Mock()
    repository.update = AsyncMock(return_value=updated)
    service = SessionService(session_repository=repository)

    result = await service.update("11111111-1111-1111-1111-111111111111", {"notes": "Great"})

    assert result.status == "IN_PROGRESS"
    repository.update.assert_awaited_once_with(
        "11111111-1111-1111-1111-111111111111", {"notes": "Great"}
    )


@pytest.mark.asyncio
async def test_session_service_list_delegates_to_repository(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.list = AsyncMock(return_value=([_session("IN_PROGRESS")], {"total": 1}))
    service = SessionService(session_repository=repository)

    items, pagination = await service.list(page=1, page_size=2, status="IN_PROGRESS")

    assert len(items) == 1
    assert pagination["total"] == 1
    repository.list.assert_awaited_once_with(page=1, page_size=2, status="IN_PROGRESS")
