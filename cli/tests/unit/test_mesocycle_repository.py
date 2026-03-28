from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.infrastructure.graphql.mutations.mesocycle import (
    ADD_MESOCYCLE_WEEK,
    ADD_PLANNED_SESSION,
    CREATE_MESOCYCLE,
    DELETE_MESOCYCLE,
    REMOVE_MESOCYCLE_WEEK,
    REMOVE_PLANNED_SESSION,
    UPDATE_MESOCYCLE,
    UPDATE_MESOCYCLE_WEEK,
    UPDATE_PLANNED_SESSION,
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


def _week_payload() -> dict[str, object]:
    return {
        "id": "22222222-2222-2222-2222-222222222222",
        "weekNumber": 1,
        "weekType": "TRAINING",
        "startDate": "2026-01-01",
        "endDate": "2026-01-07",
        "plannedSessions": [],
    }


def _planned_session_payload() -> dict[str, object]:
    return {
        "id": "33333333-3333-3333-3333-333333333333",
        "routine": {
            "id": "44444444-4444-4444-4444-444444444444",
            "name": "Push A",
        },
        "dayOfWeek": 1,
        "date": "2026-01-01",
        "notes": "Heavy compounds",
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


@pytest.mark.asyncio
async def test_repository_add_week_maps_mesocycle_week() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"addMesocycleWeek": _week_payload()})

    repository = GraphQLMesocycleRepository(client=client)
    week = await repository.add_week(
        "11111111-1111-1111-1111-111111111111",
        {
            "weekNumber": 1,
            "weekType": "TRAINING",
            "startDate": "2026-01-01",
            "endDate": "2026-01-07",
        },
    )

    assert week.week_number == 1
    client.execute.assert_awaited_once_with(
        ADD_MESOCYCLE_WEEK,
        {
            "mesocycleId": "11111111-1111-1111-1111-111111111111",
            "input": {
                "weekNumber": 1,
                "weekType": "TRAINING",
                "startDate": "2026-01-01",
                "endDate": "2026-01-07",
            },
        },
    )


@pytest.mark.asyncio
async def test_repository_update_week_maps_mesocycle_week() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"updateMesocycleWeek": _week_payload()})

    repository = GraphQLMesocycleRepository(client=client)
    week = await repository.update_week(
        "22222222-2222-2222-2222-222222222222",
        {"weekType": "DELOAD"},
    )

    assert week.id == "22222222-2222-2222-2222-222222222222"
    client.execute.assert_awaited_once_with(
        UPDATE_MESOCYCLE_WEEK,
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "input": {"weekType": "DELOAD"},
        },
    )


@pytest.mark.asyncio
async def test_repository_remove_week_maps_boolean() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"removeMesocycleWeek": True})

    repository = GraphQLMesocycleRepository(client=client)
    deleted = await repository.remove_week("22222222-2222-2222-2222-222222222222")

    assert deleted is True
    client.execute.assert_awaited_once_with(
        REMOVE_MESOCYCLE_WEEK,
        {"id": "22222222-2222-2222-2222-222222222222"},
    )


@pytest.mark.asyncio
async def test_repository_add_session_maps_planned_session() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"addPlannedSession": _planned_session_payload()})

    repository = GraphQLMesocycleRepository(client=client)
    planned_session = await repository.add_session(
        "22222222-2222-2222-2222-222222222222",
        {
            "routineId": "44444444-4444-4444-4444-444444444444",
            "dayOfWeek": 1,
            "date": "2026-01-01",
        },
    )

    assert planned_session.routine_name == "Push A"
    client.execute.assert_awaited_once_with(
        ADD_PLANNED_SESSION,
        {
            "mesocycleWeekId": "22222222-2222-2222-2222-222222222222",
            "input": {
                "routineId": "44444444-4444-4444-4444-444444444444",
                "dayOfWeek": 1,
                "date": "2026-01-01",
            },
        },
    )


@pytest.mark.asyncio
async def test_repository_update_session_maps_planned_session() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"updatePlannedSession": _planned_session_payload()})

    repository = GraphQLMesocycleRepository(client=client)
    planned_session = await repository.update_session(
        "33333333-3333-3333-3333-333333333333",
        {"notes": "Updated"},
    )

    assert planned_session.id == "33333333-3333-3333-3333-333333333333"
    client.execute.assert_awaited_once_with(
        UPDATE_PLANNED_SESSION,
        {
            "id": "33333333-3333-3333-3333-333333333333",
            "input": {"notes": "Updated"},
        },
    )


@pytest.mark.asyncio
async def test_repository_remove_session_maps_boolean() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"removePlannedSession": True})

    repository = GraphQLMesocycleRepository(client=client)
    deleted = await repository.remove_session("33333333-3333-3333-3333-333333333333")

    assert deleted is True
    client.execute.assert_awaited_once_with(
        REMOVE_PLANNED_SESSION,
        {"id": "33333333-3333-3333-3333-333333333333"},
    )
