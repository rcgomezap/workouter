from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.infrastructure.graphql.queries.insight import (
    EXERCISE_HISTORY,
    MESOCYCLE_INTENSITY_INSIGHT,
    MESOCYCLE_VOLUME_INSIGHT,
    PROGRESSIVE_OVERLOAD_INSIGHT,
)
from workouter_cli.infrastructure.repositories.insight import GraphQLInsightRepository


def _session_payload() -> dict[str, object]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "plannedSessionId": None,
        "mesocycleId": "22222222-2222-2222-2222-222222222222",
        "routineId": "33333333-3333-3333-3333-333333333333",
        "status": "COMPLETED",
        "startedAt": "2026-01-01T10:00:00Z",
        "completedAt": "2026-01-01T11:00:00Z",
        "notes": None,
        "exercises": [],
    }


@pytest.mark.asyncio
async def test_repository_volume_maps_payload() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "mesocycleVolumeInsight": {
                "mesocycleId": "22222222-2222-2222-2222-222222222222",
                "weeklyVolumes": [
                    {
                        "weekNumber": 1,
                        "muscleGroupId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                        "muscleGroupName": "Chest",
                        "setCount": 12,
                    }
                ],
                "totalSets": 12,
                "muscleGroupBreakdown": [
                    {
                        "muscleGroupId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                        "muscleGroupName": "Chest",
                        "totalSets": 12,
                    }
                ],
            }
        }
    )

    repository = GraphQLInsightRepository(client=client)
    insight = await repository.volume("22222222-2222-2222-2222-222222222222")

    assert insight.total_sets == 12
    client.execute.assert_awaited_once_with(
        MESOCYCLE_VOLUME_INSIGHT,
        {"mesocycleId": "22222222-2222-2222-2222-222222222222", "muscleGroupId": None},
    )


@pytest.mark.asyncio
async def test_repository_intensity_maps_payload() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "mesocycleIntensityInsight": {
                "mesocycleId": "22222222-2222-2222-2222-222222222222",
                "weeklyIntensities": [{"weekNumber": 1, "avgRir": 2.0}],
                "overallAvgRir": 2.0,
            }
        }
    )

    repository = GraphQLInsightRepository(client=client)
    insight = await repository.intensity("22222222-2222-2222-2222-222222222222")

    assert insight.overall_avg_rir == 2.0
    client.execute.assert_awaited_once_with(
        MESOCYCLE_INTENSITY_INSIGHT,
        {"mesocycleId": "22222222-2222-2222-2222-222222222222"},
    )


@pytest.mark.asyncio
async def test_repository_overload_maps_payload() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "progressiveOverloadInsight": {
                "exerciseId": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "mesocycleId": "22222222-2222-2222-2222-222222222222",
                "weeklyProgress": [
                    {
                        "weekNumber": 1,
                        "maxWeight": 80.0,
                        "avgReps": 10.0,
                        "avgRir": 2.0,
                    }
                ],
                "estimatedOneRepMaxProgression": [100.0],
            }
        }
    )

    repository = GraphQLInsightRepository(client=client)
    insight = await repository.overload(
        "22222222-2222-2222-2222-222222222222",
        "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    )

    assert insight.estimated_one_rep_max_progression[0] == 100.0
    client.execute.assert_awaited_once_with(
        PROGRESSIVE_OVERLOAD_INSIGHT,
        {
            "mesocycleId": "22222222-2222-2222-2222-222222222222",
            "exerciseId": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        },
    )


@pytest.mark.asyncio
async def test_repository_history_maps_payload_and_pagination() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "exerciseHistory": {
                "items": [_session_payload()],
                "total": 1,
                "page": 1,
                "pageSize": 20,
                "totalPages": 1,
            }
        }
    )

    repository = GraphQLInsightRepository(client=client)
    items, pagination = await repository.history(
        "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        page=1,
        page_size=20,
    )

    assert len(items) == 1
    assert items[0].status == "COMPLETED"
    assert pagination == {"total": 1, "page": 1, "pageSize": 20, "totalPages": 1}
    client.execute.assert_awaited_once_with(
        EXERCISE_HISTORY,
        {
            "exerciseId": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "routineId": None,
            "pagination": {"page": 1, "pageSize": 20},
        },
    )
