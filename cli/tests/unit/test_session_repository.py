from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.infrastructure.repositories.session import GraphQLSessionRepository


def _session_payload(status: str) -> dict[str, object]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "plannedSessionId": "22222222-2222-2222-2222-222222222222",
        "mesocycleId": None,
        "routineId": "33333333-3333-3333-3333-333333333333",
        "status": status,
        "startedAt": "2026-01-01T10:00:00Z",
        "completedAt": None,
        "notes": None,
        "exercises": [],
    }


@pytest.mark.asyncio
async def test_repository_start_maps_session() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"startSession": _session_payload("IN_PROGRESS")})

    repository = GraphQLSessionRepository(client=client)
    session = await repository.start("11111111-1111-1111-1111-111111111111")

    assert session.id == "11111111-1111-1111-1111-111111111111"
    assert session.status == "IN_PROGRESS"
    client.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_repository_complete_maps_session() -> None:
    payload = _session_payload("COMPLETED")
    payload["completedAt"] = "2026-01-01T11:00:00Z"

    client = AsyncMock()
    client.execute = AsyncMock(return_value={"completeSession": payload})

    repository = GraphQLSessionRepository(client=client)
    session = await repository.complete("11111111-1111-1111-1111-111111111111")

    assert session.status == "COMPLETED"
    assert session.completed_at == "2026-01-01T11:00:00Z"
    client.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_repository_update_maps_session() -> None:
    payload = _session_payload("IN_PROGRESS")
    payload["notes"] = "Solid session"

    client = AsyncMock()
    client.execute = AsyncMock(return_value={"updateSession": payload})

    repository = GraphQLSessionRepository(client=client)
    session = await repository.update(
        "11111111-1111-1111-1111-111111111111", {"notes": "Solid session"}
    )

    assert session.notes == "Solid session"
    client.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_repository_list_maps_sessions_and_pagination() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "sessions": {
                "items": [_session_payload("IN_PROGRESS")],
                "total": 1,
                "page": 1,
                "pageSize": 2,
                "totalPages": 1,
            }
        }
    )

    repository = GraphQLSessionRepository(client=client)
    items, pagination = await repository.list(page=1, page_size=2, status="IN_PROGRESS")

    assert len(items) == 1
    assert items[0].status == "IN_PROGRESS"
    assert pagination["total"] == 1
    assert pagination["pageSize"] == 2
    client.execute.assert_awaited_once()
