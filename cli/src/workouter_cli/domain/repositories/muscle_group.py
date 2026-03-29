"""Muscle group repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.exercise import MuscleGroup


class MuscleGroupRepository(Protocol):
    """Persistence contract for muscle groups."""

    async def list_all(self) -> list[MuscleGroup]:
        """List all muscle groups (17 predefined groups)."""
        ...
