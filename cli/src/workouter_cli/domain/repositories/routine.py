"""Routine repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.routine import Routine, RoutineExercise, RoutineSet


class RoutineRepository(Protocol):
    """Persistence contract for routines."""

    async def list(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Routine], dict[str, int]]:
        """List routines and return items with pagination metadata."""
        ...

    async def get(self, routine_id: str) -> Routine:
        """Get one routine by ID."""
        ...

    async def create(self, payload: dict[str, str | None]) -> Routine:
        """Create one routine."""
        ...

    async def update(self, routine_id: str, payload: dict[str, str | None]) -> Routine:
        """Update one routine."""
        ...

    async def delete(self, routine_id: str) -> bool:
        """Delete one routine."""
        ...

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
