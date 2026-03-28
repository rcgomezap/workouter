"""Exercise repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.exercise import Exercise


class ExerciseRepository(Protocol):
    """Persistence contract for exercises."""

    async def list(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Exercise], dict[str, int]]:
        """List exercises and return items with pagination metadata."""
        ...

    async def get(self, exercise_id: str) -> Exercise:
        """Get one exercise by ID."""
        ...

    async def create(self, payload: dict[str, str | None]) -> Exercise:
        """Create one exercise."""
        ...

    async def update(self, exercise_id: str, payload: dict[str, str | None]) -> Exercise:
        """Update one exercise."""
        ...

    async def delete(self, exercise_id: str) -> bool:
        """Delete one exercise."""
        ...
