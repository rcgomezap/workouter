from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.application.dto.routine import CreateRoutineInputDTO, UpdateRoutineInputDTO
from workouter_cli.application.services.routine_service import RoutineService
from workouter_cli.domain.entities.routine import Routine, RoutineExercise, RoutineSet


def _routine() -> Routine:
    return Routine(
        id="11111111-1111-1111-1111-111111111111",
        name="Push Day",
        description="Chest/Shoulders/Triceps",
        exercises=(),
    )


def _routine_exercise() -> RoutineExercise:
    return RoutineExercise(
        id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        exercise_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        exercise_name="Bench Press",
        order=1,
        superset_group=None,
        rest_seconds=120,
        notes=None,
        sets=(),
    )


def _routine_set() -> RoutineSet:
    return RoutineSet(
        id="cccccccc-cccc-cccc-cccc-cccccccccccc",
        set_number=1,
        set_type="STANDARD",
        target_reps_min=8,
        target_reps_max=10,
        target_rir=2,
        target_weight_kg=80.0,
        weight_reduction_pct=None,
        rest_seconds=120,
    )


@pytest.mark.asyncio
async def test_routine_service_crud_delegates(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.list = AsyncMock(
        return_value=([_routine()], {"total": 1, "page": 1, "pageSize": 20, "totalPages": 1})
    )
    repository.get = AsyncMock(return_value=_routine())
    repository.create = AsyncMock(return_value=_routine())
    repository.update = AsyncMock(return_value=_routine())
    repository.delete = AsyncMock(return_value=True)
    service = RoutineService(routine_repository=repository)

    items, pagination = await service.list(page=1, page_size=20)
    fetched = await service.get("11111111-1111-1111-1111-111111111111")
    created = await service.create(CreateRoutineInputDTO(name="Push Day"))
    updated = await service.update(
        "11111111-1111-1111-1111-111111111111",
        UpdateRoutineInputDTO(description="Updated"),
    )
    deleted = await service.delete("11111111-1111-1111-1111-111111111111")

    assert len(items) == 1
    assert pagination["total"] == 1
    assert fetched.name == "Push Day"
    assert created.name == "Push Day"
    assert updated.id == "11111111-1111-1111-1111-111111111111"
    assert deleted is True

    repository.list.assert_awaited_once_with(page=1, page_size=20)
    repository.get.assert_awaited_once_with("11111111-1111-1111-1111-111111111111")
    repository.create.assert_awaited_once_with({"name": "Push Day"})
    repository.update.assert_awaited_once_with(
        "11111111-1111-1111-1111-111111111111",
        {"description": "Updated"},
    )
    repository.delete.assert_awaited_once_with("11111111-1111-1111-1111-111111111111")


@pytest.mark.asyncio
async def test_routine_service_add_and_update_nested_entities(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.add_exercise = AsyncMock(return_value=_routine())
    repository.update_exercise = AsyncMock(return_value=_routine_exercise())
    repository.add_set = AsyncMock(return_value=_routine_exercise())
    repository.update_set = AsyncMock(return_value=_routine_set())
    service = RoutineService(routine_repository=repository)

    await service.add_exercise("11111111-1111-1111-1111-111111111111", {"order": 1})
    await service.update_exercise("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", {"order": 2})
    await service.add_set("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", {"setNumber": 1})
    await service.update_set("cccccccc-cccc-cccc-cccc-cccccccccccc", {"targetRepsMax": 12})

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
        "cccccccc-cccc-cccc-cccc-cccccccccccc", {"targetRepsMax": 12}
    )


@pytest.mark.asyncio
async def test_routine_service_remove_nested_entities_delegate(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.remove_exercise = AsyncMock(return_value=True)
    repository.remove_set = AsyncMock(return_value=True)
    service = RoutineService(routine_repository=repository)

    removed_exercise = await service.remove_exercise("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    removed_set = await service.remove_set("cccccccc-cccc-cccc-cccc-cccccccccccc")

    assert removed_exercise is True
    assert removed_set is True
    repository.remove_exercise.assert_awaited_once_with("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    repository.remove_set.assert_awaited_once_with("cccccccc-cccc-cccc-cccc-cccccccccccc")
