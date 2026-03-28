"""Bodyweight application service."""

from __future__ import annotations

from workouter_cli.domain.entities.bodyweight import BodyweightLog
from workouter_cli.domain.repositories.bodyweight import BodyweightRepository


class BodyweightService:
    """Bodyweight use-cases orchestration."""

    def __init__(self, bodyweight_repository: BodyweightRepository) -> None:
        self.bodyweight_repository = bodyweight_repository

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[BodyweightLog], dict[str, int]]:
        return await self.bodyweight_repository.list(
            page=page,
            page_size=page_size,
            date_from=date_from,
            date_to=date_to,
        )

    async def log(self, payload: dict[str, str | float | None]) -> BodyweightLog:
        return await self.bodyweight_repository.log(payload)

    async def update(
        self,
        bodyweight_log_id: str,
        payload: dict[str, str | float | None],
    ) -> BodyweightLog:
        return await self.bodyweight_repository.update(bodyweight_log_id, payload)

    async def delete(self, bodyweight_log_id: str) -> bool:
        return await self.bodyweight_repository.delete(bodyweight_log_id)
