from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.infrastructure.graphql.mutations.mesocycle import (
    CREATE_MESOCYCLE,
    DELETE_MESOCYCLE,
    UPDATE_MESOCYCLE,
)
from workouter_cli.infrastructure.graphql.queries.mesocycle import GET_MESOCYCLE, LIST_MESOCYCLES
from workouter_cli.infrastructure.repositories.mesocycle import GraphQLMesocycleRepository


def _mesocycle_payload() -> dict[str, object]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Hypertrophy Block",
        "description": "Upper focus",
        "startDate": "2026-01-01",
        "endDate": None,
        "status": "PLANNED",
        "weeks": [],
    }


@pytest.mark.asyncio
async def test_repository_list_maps_mesocycles_and_pagination() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "mesocycles": {
                "items": [_mesocycle_payload()],
                "total": 1,
                "page": 1,
                "pageSize": 20,
                "totalPages": 1,
            }
        }
    )

    repository = GraphQLMesocycleRepository(client=client)
    items, pagination = await repository.list(page=1, page_size=20, status="PLANNED")

    assert len(items) == 1
    assert items[0].name == "Hypertrophy Block"
    assert items[0].start_date == "2026-01-01"
    assert pagination == {"total": 1, "page": 1, "pageSize": 20, "totalPages": 1}
    client.execute.assert_awaited_once_with(
        LIST_MESOCYCLES,
        {"pagination": {"page": 1, "pageSize": 20}, "status": "PLANNED"},
    )


@pytest.mark.asyncio
async def test_repository_get_maps_mesocycle() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"mesocycle": _mesocycle_payload()})

    repository = GraphQLMesocycleRepository(client=client)
    mesocycle = await repository.get("11111111-1111-1111-1111-111111111111")

    assert mesocycle.id == "11111111-1111-1111-1111-111111111111"
    client.execute.assert_awaited_once_with(
        GET_MESOCYCLE,
        {"id": "11111111-1111-1111-1111-111111111111"},
    )


@pytest.mark.asyncio
async def test_repository_create_maps_mesocycle() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"createMesocycle": _mesocycle_payload()})

    repository = GraphQLMesocycleRepository(client=client)
    mesocycle = await repository.create({"name": "Hypertrophy Block", "startDate": "2026-01-01"})

    assert mesocycle.name == "Hypertrophy Block"
    client.execute.assert_awaited_once_with(
        CREATE_MESOCYCLE,
        {"input": {"name": "Hypertrophy Block", "startDate": "2026-01-01"}},
    )


@pytest.mark.asyncio
async def test_repository_update_maps_mesocycle() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"updateMesocycle": _mesocycle_payload()})

    repository = GraphQLMesocycleRepository(client=client)
    mesocycle = await repository.update(
        "11111111-1111-1111-1111-111111111111",
        {"status": "ACTIVE"},
    )

    assert mesocycle.status == "PLANNED"
    client.execute.assert_awaited_once_with(
        UPDATE_MESOCYCLE,
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "input": {"status": "ACTIVE"},
        },
    )


@pytest.mark.asyncio
async def test_repository_delete_maps_boolean() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"deleteMesocycle": True})

    repository = GraphQLMesocycleRepository(client=client)
    deleted = await repository.delete("11111111-1111-1111-1111-111111111111")

    assert deleted is True
    client.execute.assert_awaited_once_with(
        DELETE_MESOCYCLE,
        {"id": "11111111-1111-1111-1111-111111111111"},
    )
