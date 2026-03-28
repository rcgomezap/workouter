from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.infrastructure.graphql.mutations.session import (
    ADD_SESSION_EXERCISE,
    ADD_SESSION_SET,
    DELETE_SESSION,
    REMOVE_SESSION_EXERCISE,
    REMOVE_SESSION_SET,
    UPDATE_SESSION_EXERCISE,
    UPDATE_SESSION_SET,
)
from workouter_cli.infrastructure.graphql.queries.session import GET_SESSION, LIST_SESSIONS
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
    client.execute.assert_awaited_once_with(
        LIST_SESSIONS,
        {
            "pagination": {"page": 1, "pageSize": 2},
            "status": "IN_PROGRESS",
            "mesocycleId": None,
            "dateFrom": None,
            "dateTo": None,
        },
    )


@pytest.mark.asyncio
async def test_repository_get_maps_session() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"session": _session_payload("IN_PROGRESS")})

    repository = GraphQLSessionRepository(client=client)
    session = await repository.get("11111111-1111-1111-1111-111111111111")

    assert session.id == "11111111-1111-1111-1111-111111111111"
    client.execute.assert_awaited_once_with(
        GET_SESSION, {"id": "11111111-1111-1111-1111-111111111111"}
    )


@pytest.mark.asyncio
async def test_repository_delete_maps_boolean() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"deleteSession": True})

    repository = GraphQLSessionRepository(client=client)
    deleted = await repository.delete("11111111-1111-1111-1111-111111111111")

    assert deleted is True
    client.execute.assert_awaited_once_with(
        DELETE_SESSION,
        {"id": "11111111-1111-1111-1111-111111111111"},
    )


@pytest.mark.asyncio
async def test_repository_add_exercise_maps_session() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"addSessionExercise": _session_payload("IN_PROGRESS")})

    repository = GraphQLSessionRepository(client=client)
    session = await repository.add_exercise(
        "11111111-1111-1111-1111-111111111111",
        {
            "exerciseId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "order": 1,
        },
    )

    assert session.status == "IN_PROGRESS"
    client.execute.assert_awaited_once_with(
        ADD_SESSION_EXERCISE,
        {
            "sessionId": "11111111-1111-1111-1111-111111111111",
            "input": {
                "exerciseId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "order": 1,
            },
        },
    )


@pytest.mark.asyncio
async def test_repository_update_exercise_maps_session_exercise() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "updateSessionExercise": {
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

    repository = GraphQLSessionRepository(client=client)
    session_exercise = await repository.update_exercise(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", {"order": 2}
    )

    assert session_exercise.order == 2
    assert session_exercise.exercise_name == "Bench Press"
    client.execute.assert_awaited_once_with(
        UPDATE_SESSION_EXERCISE,
        {"id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "input": {"order": 2}},
    )


@pytest.mark.asyncio
async def test_repository_remove_exercise_maps_boolean() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"removeSessionExercise": True})

    repository = GraphQLSessionRepository(client=client)
    deleted = await repository.remove_exercise("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

    assert deleted is True
    client.execute.assert_awaited_once_with(
        REMOVE_SESSION_EXERCISE,
        {"id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"},
    )


@pytest.mark.asyncio
async def test_repository_add_set_maps_session_exercise() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "addSessionSet": {
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
                        "targetReps": 10,
                        "targetRir": 2,
                        "targetWeightKg": 80.0,
                        "actualReps": None,
                        "actualRir": None,
                        "actualWeightKg": None,
                        "weightReductionPct": None,
                        "restSeconds": 120,
                        "performedAt": None,
                    }
                ],
            }
        }
    )

    repository = GraphQLSessionRepository(client=client)
    session_exercise = await repository.add_set(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        {"setNumber": 1, "setType": "STANDARD"},
    )

    assert len(session_exercise.sets) == 1
    assert session_exercise.sets[0].set_type == "STANDARD"
    client.execute.assert_awaited_once_with(
        ADD_SESSION_SET,
        {
            "sessionExerciseId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "input": {"setNumber": 1, "setType": "STANDARD"},
        },
    )


@pytest.mark.asyncio
async def test_repository_update_set_maps_session_set() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "updateSessionSet": {
                "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                "setNumber": 1,
                "setType": "STANDARD",
                "targetReps": 12,
                "targetRir": 1,
                "targetWeightKg": 82.5,
                "actualReps": None,
                "actualRir": None,
                "actualWeightKg": None,
                "weightReductionPct": None,
                "restSeconds": 120,
                "performedAt": None,
            }
        }
    )

    repository = GraphQLSessionRepository(client=client)
    session_set = await repository.update_set(
        "cccccccc-cccc-cccc-cccc-cccccccccccc", {"targetReps": 12}
    )

    assert session_set.target_reps == 12
    client.execute.assert_awaited_once_with(
        UPDATE_SESSION_SET,
        {"id": "cccccccc-cccc-cccc-cccc-cccccccccccc", "input": {"targetReps": 12}},
    )


@pytest.mark.asyncio
async def test_repository_remove_set_maps_boolean() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(return_value={"removeSessionSet": True})

    repository = GraphQLSessionRepository(client=client)
    deleted = await repository.remove_set("cccccccc-cccc-cccc-cccc-cccccccccccc")

    assert deleted is True
    client.execute.assert_awaited_once_with(
        REMOVE_SESSION_SET,
        {"id": "cccccccc-cccc-cccc-cccc-cccccccccccc"},
    )
