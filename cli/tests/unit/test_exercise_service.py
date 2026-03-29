from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.application.services.exercise_service import ExerciseService


@pytest.mark.asyncio
async def test_service_list_uses_default_pagination() -> None:
    repo = AsyncMock()
    repo.list = AsyncMock(
        return_value=([], {"total": 0, "page": 1, "pageSize": 20, "totalPages": 0})
    )
    service = ExerciseService(exercise_repository=repo)

    await service.list()

    repo.list.assert_awaited_once_with(page=1, page_size=20, muscle_group_id=None)


@pytest.mark.asyncio
async def test_service_list_passes_muscle_group_filter() -> None:
    repo = AsyncMock()
    repo.list = AsyncMock(
        return_value=([], {"total": 0, "page": 1, "pageSize": 20, "totalPages": 0})
    )
    service = ExerciseService(exercise_repository=repo)

    await service.list(muscle_group_id="11111111-1111-1111-1111-111111111111")

    repo.list.assert_awaited_once_with(
        page=1,
        page_size=20,
        muscle_group_id="11111111-1111-1111-1111-111111111111",
    )


@pytest.mark.asyncio
async def test_service_create_passes_serialized_payload() -> None:
    repo = AsyncMock()
    repo.create = AsyncMock(return_value=object())
    service = ExerciseService(exercise_repository=repo)

    from workouter_cli.application.dto.exercise import CreateExerciseInputDTO

    dto = CreateExerciseInputDTO(name="Bench Press", equipment="Barbell")
    await service.create(dto)

    repo.create.assert_awaited_once_with({"name": "Bench Press", "equipment": "Barbell"})


@pytest.mark.asyncio
async def test_assign_muscle_groups_success() -> None:
    """Test assigning muscle groups to an exercise."""
    repo = AsyncMock()
    from workouter_cli.domain.entities.exercise import Exercise

    mock_exercise = Exercise(
        id="ex1",
        name="Bench Press",
        description=None,
        equipment=None,
        muscle_groups=(),
    )
    repo.assign_muscle_groups = AsyncMock(return_value=mock_exercise)
    service = ExerciseService(exercise_repository=repo)

    result = await service.assign_muscle_groups(
        "ex1",
        primary_ids=["mg1", "mg2"],
        secondary_ids=["mg3"],
    )

    assert result == mock_exercise
    repo.assign_muscle_groups.assert_awaited_once_with(
        "ex1",
        [
            {"muscleGroupId": "mg1", "role": "PRIMARY"},
            {"muscleGroupId": "mg2", "role": "PRIMARY"},
            {"muscleGroupId": "mg3", "role": "SECONDARY"},
        ],
    )


@pytest.mark.asyncio
async def test_assign_muscle_groups_rejects_duplicate_roles() -> None:
    """Test that assigning same muscle group to both roles raises error."""
    repo = AsyncMock()
    service = ExerciseService(exercise_repository=repo)

    with pytest.raises(ValueError, match="cannot be both PRIMARY and SECONDARY"):
        await service.assign_muscle_groups(
            "ex1",
            primary_ids=["mg1", "mg2"],
            secondary_ids=["mg2"],  # mg2 appears in both!
        )

    repo.assign_muscle_groups.assert_not_awaited()


@pytest.mark.asyncio
async def test_assign_muscle_groups_rejects_duplicate_primary_ids() -> None:
    """Test duplicate PRIMARY IDs are rejected before repository call."""
    repo = AsyncMock()
    service = ExerciseService(exercise_repository=repo)

    with pytest.raises(ValueError, match="Duplicate muscle group IDs found in PRIMARY"):
        await service.assign_muscle_groups(
            "ex1",
            primary_ids=["mg1", "mg1"],
            secondary_ids=[],
        )

    repo.assign_muscle_groups.assert_not_awaited()


@pytest.mark.asyncio
async def test_assign_muscle_groups_rejects_duplicate_secondary_ids() -> None:
    """Test duplicate SECONDARY IDs are rejected before repository call."""
    repo = AsyncMock()
    service = ExerciseService(exercise_repository=repo)

    with pytest.raises(ValueError, match="Duplicate muscle group IDs found in SECONDARY"):
        await service.assign_muscle_groups(
            "ex1",
            primary_ids=[],
            secondary_ids=["mg2", "mg2"],
        )

    repo.assign_muscle_groups.assert_not_awaited()
