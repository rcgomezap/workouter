"""Exercise application service."""

from __future__ import annotations

from workouter_cli.application.dto.exercise import CreateExerciseInputDTO, UpdateExerciseInputDTO
from workouter_cli.domain.entities.exercise import Exercise
from workouter_cli.domain.repositories.exercise import ExerciseRepository


class ExerciseService:
    """Exercise use-cases orchestration and business defaults."""

    def __init__(self, exercise_repository: ExerciseRepository) -> None:
        self.exercise_repository = exercise_repository

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        muscle_group_id: str | None = None,
    ) -> tuple[list[Exercise], dict[str, int]]:
        return await self.exercise_repository.list(
            page=page,
            page_size=page_size,
            muscle_group_id=muscle_group_id,
        )

    async def get(self, exercise_id: str) -> Exercise:
        return await self.exercise_repository.get(exercise_id)

    async def create(self, payload: CreateExerciseInputDTO) -> Exercise:
        data = payload.model_dump(exclude_none=True)
        return await self.exercise_repository.create(data)

    async def update(self, exercise_id: str, payload: UpdateExerciseInputDTO) -> Exercise:
        data = payload.model_dump(exclude_none=True)
        return await self.exercise_repository.update(exercise_id, data)

    async def delete(self, exercise_id: str) -> bool:
        return await self.exercise_repository.delete(exercise_id)
