"""Insights application service."""

from __future__ import annotations

from workouter_cli.domain.entities.insight import (
    IntensityInsight,
    ProgressiveOverloadInsight,
    VolumeInsight,
)
from workouter_cli.domain.entities.session import Session
from workouter_cli.domain.repositories.insight import InsightRepository


class InsightService:
    """Insight use-cases orchestration."""

    def __init__(self, insight_repository: InsightRepository) -> None:
        self.insight_repository = insight_repository

    async def volume(self, mesocycle_id: str, muscle_group_id: str | None = None) -> VolumeInsight:
        return await self.insight_repository.volume(
            mesocycle_id=mesocycle_id,
            muscle_group_id=muscle_group_id,
        )

    async def intensity(self, mesocycle_id: str) -> IntensityInsight:
        return await self.insight_repository.intensity(mesocycle_id=mesocycle_id)

    async def overload(self, mesocycle_id: str, exercise_id: str) -> ProgressiveOverloadInsight:
        return await self.insight_repository.overload(
            mesocycle_id=mesocycle_id,
            exercise_id=exercise_id,
        )

    async def history(
        self,
        exercise_id: str,
        routine_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Session], dict[str, int]]:
        return await self.insight_repository.history(
            exercise_id=exercise_id,
            routine_id=routine_id,
            page=page,
            page_size=page_size,
        )
