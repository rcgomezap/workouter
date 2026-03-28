"""Mesocycle application service."""

from __future__ import annotations

from workouter_cli.application.dto.mesocycle import (
    AddMesocycleWeekInputDTO,
    AddPlannedSessionInputDTO,
    CreateMesocycleInputDTO,
    UpdateMesocycleWeekInputDTO,
    UpdateMesocycleInputDTO,
    UpdatePlannedSessionInputDTO,
)
from workouter_cli.domain.entities.mesocycle import (
    Mesocycle,
    MesocyclePlannedSession,
    MesocycleWeek,
)
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

    async def add_week(self, mesocycle_id: str, payload: AddMesocycleWeekInputDTO) -> MesocycleWeek:
        data = payload.model_dump(mode="json", by_alias=True, exclude_none=True)
        return await self.mesocycle_repository.add_week(mesocycle_id, data)

    async def update_week(
        self, week_id: str, payload: UpdateMesocycleWeekInputDTO
    ) -> MesocycleWeek:
        data = payload.model_dump(mode="json", by_alias=True, exclude_none=True)
        return await self.mesocycle_repository.update_week(week_id, data)

    async def remove_week(self, week_id: str) -> bool:
        return await self.mesocycle_repository.remove_week(week_id)

    async def add_session(
        self,
        mesocycle_week_id: str,
        payload: AddPlannedSessionInputDTO,
    ) -> MesocyclePlannedSession:
        data = payload.model_dump(mode="json", by_alias=True, exclude_none=True)
        return await self.mesocycle_repository.add_session(mesocycle_week_id, data)

    async def update_session(
        self,
        session_id: str,
        payload: UpdatePlannedSessionInputDTO,
    ) -> MesocyclePlannedSession:
        data = payload.model_dump(mode="json", by_alias=True, exclude_none=True)
        return await self.mesocycle_repository.update_session(session_id, data)

    async def remove_session(self, session_id: str) -> bool:
        return await self.mesocycle_repository.remove_session(session_id)
