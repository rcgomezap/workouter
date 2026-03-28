from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.infrastructure.graphql.queries.exercise import LIST_EXERCISES
from workouter_cli.infrastructure.repositories.exercise import GraphQLExerciseRepository


@pytest.mark.asyncio
async def test_repository_list_maps_items_and_pagination() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "exercises": {
                "items": [
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "name": "Bench Press",
                        "description": "Chest press",
                        "equipment": "Barbell",
                        "muscleGroups": [
                            {
                                "muscleGroup": {
                                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                    "name": "Chest",
                                },
                                "role": "PRIMARY",
                            }
                        ],
                    }
                ],
                "total": 1,
                "page": 1,
                "pageSize": 20,
                "totalPages": 1,
            }
        }
    )

    repository = GraphQLExerciseRepository(client=client)
    items, pagination = await repository.list(page=1, page_size=20)

    assert len(items) == 1
    assert items[0].name == "Bench Press"
    assert items[0].muscle_groups[0].muscle_group.name == "Chest"
    assert pagination["total"] == 1
    assert pagination["pageSize"] == 20
    client.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_repository_list_passes_muscle_group_id_variable() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "exercises": {
                "items": [],
                "total": 0,
                "page": 1,
                "pageSize": 20,
                "totalPages": 0,
            }
        }
    )

    repository = GraphQLExerciseRepository(client=client)
    await repository.list(
        page=1, page_size=20, muscle_group_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    )

    client.execute.assert_awaited_once_with(
        LIST_EXERCISES,
        {
            "pagination": {"page": 1, "pageSize": 20},
            "muscleGroupId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        },
    )
