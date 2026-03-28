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
