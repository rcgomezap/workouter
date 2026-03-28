"""Mesocycle application service."""

from __future__ import annotations

from workouter_cli.application.dto.mesocycle import (
    CreateMesocycleInputDTO,
    UpdateMesocycleInputDTO,
)
from workouter_cli.domain.entities.mesocycle import Mesocycle
from workouter_cli.domain.repositories.mesocycle import MesocycleRepository


class MesocycleService:
    """Mesocycle lifecycle use-cases orchestration."""

    def __init__(self, mesocycle_repository: MesocycleRepository) -> None:
        self.mesocycle_repository = mesocycle_repository

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Mesocycle], dict[str, int]]:
        return await self.mesocycle_repository.list(
            page=page,
            page_size=page_size,
            status=status,
        )

    async def get(self, mesocycle_id: str) -> Mesocycle:
        return await self.mesocycle_repository.get(mesocycle_id)

    async def create(self, payload: CreateMesocycleInputDTO) -> Mesocycle:
        data = payload.model_dump(mode="json", by_alias=True, exclude_none=True)
        return await self.mesocycle_repository.create(data)

    async def update(self, mesocycle_id: str, payload: UpdateMesocycleInputDTO) -> Mesocycle:
        data = payload.model_dump(mode="json", by_alias=True, exclude_none=True)
        return await self.mesocycle_repository.update(mesocycle_id, data)

    async def delete(self, mesocycle_id: str) -> bool:
        return await self.mesocycle_repository.delete(mesocycle_id)
