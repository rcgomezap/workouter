"""Routine repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.routine import Routine, RoutineExercise, RoutineSet


class RoutineRepository(Protocol):
    """Persistence contract for routines."""

    async def add_exercise(self, routine_id: str, payload: dict[str, object]) -> Routine:
        """Add one exercise to a routine."""
        ...

    async def update_exercise(
        self, routine_exercise_id: str, payload: dict[str, object]
    ) -> RoutineExercise:
        """Update one routine exercise and return its latest state."""
        ...

    async def remove_exercise(self, routine_exercise_id: str) -> bool:
        """Remove one exercise from a routine."""
        ...

    async def add_set(
        self, routine_exercise_id: str, payload: dict[str, object]
    ) -> RoutineExercise:
        """Add one set to a routine exercise and return latest state."""
        ...

    async def update_set(self, set_id: str, payload: dict[str, object]) -> RoutineSet:
        """Update one routine set."""
        ...

    async def remove_set(self, set_id: str) -> bool:
        """Remove one set from a routine exercise."""
        ...
