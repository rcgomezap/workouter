"""Exercise application service."""

from __future__ import annotations

from collections.abc import Sequence

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

    async def assign_muscle_groups(
        self,
        exercise_id: str,
        primary_ids: Sequence[str],
        secondary_ids: Sequence[str],
    ) -> Exercise:
        """
        Assign muscle groups to an exercise.

        Replaces all existing muscle group assignments atomically.

        Args:
            exercise_id: UUID of the exercise
            primary_ids: List of muscle group UUIDs with PRIMARY role
            secondary_ids: List of muscle group UUIDs with SECONDARY role

        Returns:
            Updated exercise with new muscle group assignments

        Raises:
            ValueError: If same muscle group appears in both roles
        """
        # Validate no duplicates between primary and secondary
        primary_set: set[str] = set(primary_ids)
        secondary_set: set[str] = set(secondary_ids)
        overlap = primary_set & secondary_set

        if overlap:
            raise ValueError(f"Muscle group(s) cannot be both PRIMARY and SECONDARY: {overlap}")

        # Build assignments list
        assignments: list[dict[str, str]] = []
        for mg_id in primary_ids:
            assignments.append({"muscleGroupId": mg_id, "role": "PRIMARY"})
        for mg_id in secondary_ids:
            assignments.append({"muscleGroupId": mg_id, "role": "SECONDARY"})

        return await self.exercise_repository.assign_muscle_groups(
            exercise_id,
            assignments,
        )
