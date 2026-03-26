from datetime import date
from uuid import UUID

from app.application.dto.bodyweight import (
    BodyweightLogDTO,
    LogBodyweightInput,
    PaginatedBodyweightLogs,
    UpdateBodyweightInput,
)
from app.application.dto.pagination import PaginationInput
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.bodyweight import BodyweightLog
from app.domain.exceptions import EntityNotFoundException


class BodyweightService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_bodyweight_log(self, id: UUID) -> BodyweightLogDTO:
        async with self.uow:
            log = await self.uow.bodyweight_repository.get_by_id(id)
            if not log:
                raise EntityNotFoundException("BodyweightLog", id)
            return self._map_to_dto(log)

    async def list_bodyweight_logs(
        self,
        pagination: PaginationInput,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> PaginatedBodyweightLogs:
        async with self.uow:
            offset = (pagination.page - 1) * pagination.page_size
            limit = pagination.page_size

            logs = await self.uow.bodyweight_repository.list_by_date_range(
                date_from=date_from,
                date_to=date_to,
                offset=offset,
                limit=limit,
            )

            total = await self.uow.bodyweight_repository.count_by_date_range(
                date_from=date_from,
                date_to=date_to,
            )

            return PaginatedBodyweightLogs(
                items=[self._map_to_dto(log) for log in logs],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size,
            )

    async def log_bodyweight(self, input: LogBodyweightInput) -> BodyweightLogDTO:
        async with self.uow:
            log = BodyweightLog(
                weight_kg=input.weight_kg, recorded_at=input.recorded_at, notes=input.notes
            )
            await self.uow.bodyweight_repository.add(log)
            await self.uow.commit()
            return self._map_to_dto(log)

    async def update_bodyweight_log(
        self, id: UUID, input: UpdateBodyweightInput
    ) -> BodyweightLogDTO:
        async with self.uow:
            log = await self.uow.bodyweight_repository.get_by_id(id)
            if not log:
                raise EntityNotFoundException("BodyweightLog", id)

            if input.weight_kg is not None:
                log.weight_kg = input.weight_kg
            if input.recorded_at is not None:
                log.recorded_at = input.recorded_at
            if input.notes is not None:
                log.notes = input.notes

            await self.uow.bodyweight_repository.update(log)
            await self.uow.commit()
            return self._map_to_dto(log)

    async def delete_bodyweight_log(self, id: UUID) -> bool:
        async with self.uow:
            success = await self.uow.bodyweight_repository.delete(id)
            if not success:
                raise EntityNotFoundException("BodyweightLog", id)
            await self.uow.commit()
            return True

    def _map_to_dto(self, log: BodyweightLog) -> BodyweightLogDTO:
        return BodyweightLogDTO(
            id=log.id,
            weight_kg=log.weight_kg,
            recorded_at=log.recorded_at,
            notes=log.notes,
            created_at=log.created_at,
        )
