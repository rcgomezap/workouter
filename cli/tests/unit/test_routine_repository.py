from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.infrastructure.graphql.mutations.routine import (
    ADD_ROUTINE_EXERCISE,
    ADD_ROUTINE_SET,
    REMOVE_ROUTINE_EXERCISE,
    REMOVE_ROUTINE_SET,
    UPDATE_ROUTINE_EXERCISE,
    UPDATE_ROUTINE_SET,
)
from workouter_cli.infrastructure.repositories.routine import GraphQLRoutineRepository


def _routine_payload() -> dict[str, object]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Push Day",
        "description": "Chest/Shoulders/Triceps",
        "exercises": [],
    }


@pytest.mark.asyncio
async def test_repository_add_exercise_maps_routine() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"addRoutineExercise": _routine_payload()})

    repository = GraphQLRoutineRepository(client=client)
    routine = await repository.add_exercise(
        "11111111-1111-1111-1111-111111111111",
        {
            "exerciseId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "order": 1,
        },
    )

    assert routine.name == "Push Day"
    client.execute.assert_awaited_once_with(
        ADD_ROUTINE_EXERCISE,
        {
            "routineId": "11111111-1111-1111-1111-111111111111",
            "input": {
                "exerciseId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "order": 1,
            },
        },
    )


@pytest.mark.asyncio
async def test_repository_update_exercise_maps_routine_exercise() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "updateRoutineExercise": {
                "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "exercise": {
                    "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                    "name": "Bench Press",
                },
                "order": 2,
                "supersetGroup": None,
                "restSeconds": 120,
                "notes": "Heavy",
                "sets": [],
            }
        }
    )

    repository = GraphQLRoutineRepository(client=client)
    routine_exercise = await repository.update_exercise(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", {"order": 2}
    )

    assert routine_exercise.order == 2
    assert routine_exercise.exercise_name == "Bench Press"
    client.execute.assert_awaited_once_with(
        UPDATE_ROUTINE_EXERCISE,
        {"id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "input": {"order": 2}},
    )


@pytest.mark.asyncio
async def test_repository_remove_exercise_maps_boolean() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"removeRoutineExercise": True})

    repository = GraphQLRoutineRepository(client=client)
    deleted = await repository.remove_exercise("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

    assert deleted is True
    client.execute.assert_awaited_once_with(
        REMOVE_ROUTINE_EXERCISE,
        {"id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"},
    )


@pytest.mark.asyncio
async def test_repository_add_set_maps_routine_exercise() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "addRoutineSet": {
                "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "exercise": {
                    "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                    "name": "Bench Press",
                },
                "order": 1,
                "supersetGroup": None,
                "restSeconds": 120,
                "notes": None,
                "sets": [
                    {
                        "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                        "setNumber": 1,
                        "setType": "STANDARD",
                        "targetRepsMin": 8,
                        "targetRepsMax": 10,
                        "targetRir": 2,
                        "targetWeightKg": 80.0,
                        "weightReductionPct": None,
                        "restSeconds": 120,
                    }
                ],
            }
        }
    )

    repository = GraphQLRoutineRepository(client=client)
    routine_exercise = await repository.add_set(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        {"setNumber": 1, "setType": "STANDARD"},
    )

    assert len(routine_exercise.sets) == 1
    assert routine_exercise.sets[0].set_type == "STANDARD"
    client.execute.assert_awaited_once_with(
        ADD_ROUTINE_SET,
        {
            "routineExerciseId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "input": {"setNumber": 1, "setType": "STANDARD"},
        },
    )


@pytest.mark.asyncio
async def test_repository_update_set_maps_routine_set() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "updateRoutineSet": {
                "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                "setNumber": 1,
                "setType": "STANDARD",
                "targetRepsMin": 8,
                "targetRepsMax": 12,
                "targetRir": 1,
                "targetWeightKg": 82.5,
                "weightReductionPct": None,
                "restSeconds": 120,
            }
        }
    )

    repository = GraphQLRoutineRepository(client=client)
    routine_set = await repository.update_set(
        "cccccccc-cccc-cccc-cccc-cccccccccccc", {"targetRepsMax": 12}
    )

    assert routine_set.target_reps_max == 12
    client.execute.assert_awaited_once_with(
        UPDATE_ROUTINE_SET,
        {"id": "cccccccc-cccc-cccc-cccc-cccccccccccc", "input": {"targetRepsMax": 12}},
    )


@pytest.mark.asyncio
async def test_repository_remove_set_maps_boolean() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"removeRoutineSet": True})

    repository = GraphQLRoutineRepository(client=client)
    deleted = await repository.remove_set("cccccccc-cccc-cccc-cccc-cccccccccccc")

    assert deleted is True
    client.execute.assert_awaited_once_with(
        REMOVE_ROUTINE_SET,
        {"id": "cccccccc-cccc-cccc-cccc-cccccccccccc"},
    )
