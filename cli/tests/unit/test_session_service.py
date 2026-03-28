from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.application.services.session_service import SessionService
from workouter_cli.domain.entities.session import Session, SessionExercise, SessionSet


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


def _session_exercise() -> SessionExercise:
    return SessionExercise(
        id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        exercise_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        exercise_name="Bench Press",
        order=1,
        superset_group=None,
        rest_seconds=120,
        notes=None,
        sets=(),
    )


def _session_set() -> SessionSet:
    return SessionSet(
        id="cccccccc-cccc-cccc-cccc-cccccccccccc",
        set_number=1,
        set_type="STANDARD",
        target_reps=10,
        target_rir=2,
        target_weight_kg=80.0,
        actual_reps=None,
        actual_rir=None,
        actual_weight_kg=None,
        weight_reduction_pct=None,
        rest_seconds=120,
        performed_at=None,
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

    items, pagination = await service.list(
        page=1,
        page_size=2,
        status="IN_PROGRESS",
        mesocycle_id="22222222-2222-2222-2222-222222222222",
        date_from="2026-01-01",
        date_to="2026-01-31",
    )

    assert len(items) == 1
    assert pagination["total"] == 1
    repository.list.assert_awaited_once_with(
        page=1,
        page_size=2,
        status="IN_PROGRESS",
        mesocycle_id="22222222-2222-2222-2222-222222222222",
        date_from="2026-01-01",
        date_to="2026-01-31",
    )


@pytest.mark.asyncio
async def test_session_service_add_and_update_nested_entities(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.add_exercise = AsyncMock(return_value=_session("IN_PROGRESS"))
    repository.update_exercise = AsyncMock(return_value=_session_exercise())
    repository.add_set = AsyncMock(return_value=_session_exercise())
    repository.update_set = AsyncMock(return_value=_session_set())
    repository.log_set = AsyncMock(return_value=_session_set())
    service = SessionService(session_repository=repository)

    await service.add_exercise("11111111-1111-1111-1111-111111111111", {"order": 1})
    await service.update_exercise("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", {"order": 2})
    await service.add_set("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", {"setNumber": 1})
    await service.update_set("cccccccc-cccc-cccc-cccc-cccccccccccc", {"targetReps": 12})
    await service.log_set(
        "cccccccc-cccc-cccc-cccc-cccccccccccc",
        {"actualReps": 10, "actualWeightKg": 82.5},
    )

    repository.add_exercise.assert_awaited_once_with(
        "11111111-1111-1111-1111-111111111111", {"order": 1}
    )
    repository.update_exercise.assert_awaited_once_with(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", {"order": 2}
    )
    repository.add_set.assert_awaited_once_with(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", {"setNumber": 1}
    )
    repository.update_set.assert_awaited_once_with(
        "cccccccc-cccc-cccc-cccc-cccccccccccc", {"targetReps": 12}
    )
    repository.log_set.assert_awaited_once_with(
        "cccccccc-cccc-cccc-cccc-cccccccccccc",
        {"actualReps": 10, "actualWeightKg": 82.5},
    )


@pytest.mark.asyncio
async def test_session_service_get_and_delete_delegate(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.get = AsyncMock(return_value=_session("PLANNED"))
    repository.delete = AsyncMock(return_value=True)
    service = SessionService(session_repository=repository)

    fetched = await service.get("11111111-1111-1111-1111-111111111111")
    deleted = await service.delete("11111111-1111-1111-1111-111111111111")

    assert fetched.status == "PLANNED"
    assert deleted is True
    repository.get.assert_awaited_once_with("11111111-1111-1111-1111-111111111111")
    repository.delete.assert_awaited_once_with("11111111-1111-1111-1111-111111111111")


@pytest.mark.asyncio
async def test_session_service_remove_nested_entities_delegate(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.remove_exercise = AsyncMock(return_value=True)
    repository.remove_set = AsyncMock(return_value=True)
    service = SessionService(session_repository=repository)

    removed_exercise = await service.remove_exercise("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    removed_set = await service.remove_set("cccccccc-cccc-cccc-cccc-cccccccccccc")

    assert removed_exercise is True
    assert removed_set is True
    repository.remove_exercise.assert_awaited_once_with("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    repository.remove_set.assert_awaited_once_with("cccccccc-cccc-cccc-cccc-cccccccccccc")
