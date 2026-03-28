"""Routine application service."""

from __future__ import annotations

from workouter_cli.domain.entities.routine import Routine, RoutineExercise, RoutineSet
from workouter_cli.domain.repositories.routine import RoutineRepository


class RoutineService:
    """Routine composition use-cases orchestration."""

    def __init__(self, routine_repository: RoutineRepository) -> None:
        self.routine_repository = routine_repository

    async def add_exercise(self, routine_id: str, payload: dict[str, object]) -> Routine:
        return await self.routine_repository.add_exercise(routine_id, payload)

    async def update_exercise(
        self, routine_exercise_id: str, payload: dict[str, object]
    ) -> RoutineExercise:
        return await self.routine_repository.update_exercise(routine_exercise_id, payload)

    async def remove_exercise(self, routine_exercise_id: str) -> bool:
        return await self.routine_repository.remove_exercise(routine_exercise_id)

    async def add_set(
        self, routine_exercise_id: str, payload: dict[str, object]
    ) -> RoutineExercise:
        return await self.routine_repository.add_set(routine_exercise_id, payload)

    async def update_set(self, set_id: str, payload: dict[str, object]) -> RoutineSet:
        return await self.routine_repository.update_set(set_id, payload)

    async def remove_set(self, set_id: str) -> bool:
        return await self.routine_repository.remove_set(set_id)
