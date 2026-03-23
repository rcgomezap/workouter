from typing import Sequence
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.domain.entities.mesocycle import Mesocycle
from app.domain.enums import MesocycleStatus
from app.domain.repositories.mesocycle import MesocycleRepository
from app.infrastructure.database.models.mesocycle import MesocycleTable, MesocycleWeekTable
from app.infrastructure.database.models.session import PlannedSessionTable
from app.infrastructure.database.repositories.base import SQLAlchemyBaseRepository


class SQLAlchemyMesocycleRepository(
    SQLAlchemyBaseRepository[Mesocycle, MesocycleTable], MesocycleRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MesocycleTable)

    async def get_by_id(self, id: UUID) -> Mesocycle | None:
        stmt = (
            select(MesocycleTable)
            .where(MesocycleTable.id == id)
            .options(
                selectinload(MesocycleTable.weeks).selectinload(
                    MesocycleWeekTable.planned_sessions
                ).selectinload(
                    PlannedSessionTable.routine
                )
            )
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            return self._to_domain(model_obj)
        return None

    async def list_by_status(
        self, status: MesocycleStatus, offset: int = 0, limit: int = 20
    ) -> Sequence[Mesocycle]:
        stmt = (
            select(MesocycleTable)
            .where(MesocycleTable.status == status)
            .offset(offset)
            .limit(limit)
            .order_by(MesocycleTable.start_date.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def count_by_status(self, status: MesocycleStatus) -> int:
        stmt = select(func.count()).select_from(MesocycleTable).where(MesocycleTable.status == status)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def count_total(self) -> int:
        stmt = select(func.count()).select_from(MesocycleTable)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    def _to_domain(self, model_obj: MesocycleTable) -> Mesocycle:
        return Mesocycle.model_validate(model_obj)

    def _to_model(self, entity: Mesocycle) -> MesocycleTable:
        return MesocycleTable(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            start_date=entity.start_date,
            end_date=entity.end_date,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _update_model(self, model_obj: MesocycleTable, entity: Mesocycle) -> None:
        model_obj.name = entity.name
        model_obj.description = entity.description
        model_obj.start_date = entity.start_date
        model_obj.end_date = entity.end_date
        model_obj.status = entity.status
        model_obj.updated_at = entity.updated_at
