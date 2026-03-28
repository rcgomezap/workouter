"""Insights repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.insight import (
    IntensityInsight,
    ProgressiveOverloadInsight,
    VolumeInsight,
)
from workouter_cli.domain.entities.session import Session


class InsightRepository(Protocol):
    """Persistence contract for analytical insight queries."""

    async def volume(self, mesocycle_id: str, muscle_group_id: str | None = None) -> VolumeInsight:
        """Get mesocycle volume insight."""
        ...

    async def intensity(self, mesocycle_id: str) -> IntensityInsight:
        """Get mesocycle intensity insight."""
        ...

    async def overload(self, mesocycle_id: str, exercise_id: str) -> ProgressiveOverloadInsight:
        """Get progressive overload insight for one exercise."""
        ...

    async def history(
        self,
        exercise_id: str,
        routine_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Session], dict[str, int]]:
        """Get exercise history sessions and pagination metadata."""
        ...
