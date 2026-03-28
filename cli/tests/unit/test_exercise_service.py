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
