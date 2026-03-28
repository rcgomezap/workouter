from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.infrastructure.graphql.mutations.bodyweight import (
    DELETE_BODYWEIGHT_LOG,
    LOG_BODYWEIGHT,
    UPDATE_BODYWEIGHT_LOG,
)
from workouter_cli.infrastructure.graphql.queries.bodyweight import LIST_BODYWEIGHT_LOGS
from workouter_cli.infrastructure.repositories.bodyweight import GraphQLBodyweightRepository


def _bodyweight_payload() -> dict[str, object]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "weightKg": 80.5,
        "recordedAt": "2026-01-01T08:00:00Z",
        "notes": "Morning",
        "createdAt": "2026-01-01T08:00:00Z",
    }


@pytest.mark.asyncio
async def test_repository_list_maps_logs_and_pagination() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "bodyweightLogs": {
                "items": [_bodyweight_payload()],
                "total": 1,
                "page": 1,
                "pageSize": 20,
                "totalPages": 1,
            }
        }
    )

    repository = GraphQLBodyweightRepository(client=client)
    items, pagination = await repository.list(page=1, page_size=20)

    assert len(items) == 1
    assert items[0].weight_kg == 80.5
    assert pagination == {"total": 1, "page": 1, "pageSize": 20, "totalPages": 1}
    client.execute.assert_awaited_once_with(
        LIST_BODYWEIGHT_LOGS,
        {"pagination": {"page": 1, "pageSize": 20}, "dateFrom": None, "dateTo": None},
    )


@pytest.mark.asyncio
async def test_repository_log_maps_entry() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"logBodyweight": _bodyweight_payload()})

    repository = GraphQLBodyweightRepository(client=client)
    item = await repository.log({"weightKg": 80.5, "notes": "Morning"})

    assert item.notes == "Morning"
    client.execute.assert_awaited_once_with(
        LOG_BODYWEIGHT,
        {"input": {"weightKg": 80.5, "notes": "Morning"}},
    )


@pytest.mark.asyncio
async def test_repository_update_maps_entry() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"updateBodyweightLog": _bodyweight_payload()})

    repository = GraphQLBodyweightRepository(client=client)
    item = await repository.update("11111111-1111-1111-1111-111111111111", {"notes": "Updated"})

    assert item.id == "11111111-1111-1111-1111-111111111111"
    client.execute.assert_awaited_once_with(
        UPDATE_BODYWEIGHT_LOG,
        {"id": "11111111-1111-1111-1111-111111111111", "input": {"notes": "Updated"}},
    )


@pytest.mark.asyncio
async def test_repository_delete_maps_boolean() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"deleteBodyweightLog": True})

    repository = GraphQLBodyweightRepository(client=client)
    deleted = await repository.delete("11111111-1111-1111-1111-111111111111")

    assert deleted is True
    client.execute.assert_awaited_once_with(
        DELETE_BODYWEIGHT_LOG,
        {"id": "11111111-1111-1111-1111-111111111111"},
    )
