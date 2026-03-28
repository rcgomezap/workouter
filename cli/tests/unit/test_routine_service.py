from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

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
