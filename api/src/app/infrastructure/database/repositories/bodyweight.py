from collections.abc import Sequence
from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.bodyweight import BodyweightLog
from app.domain.repositories.bodyweight import BodyweightRepository
from app.infrastructure.database.models.bodyweight import BodyweightLogTable
from app.infrastructure.database.repositories.base import SQLAlchemyBaseRepository


class SQLAlchemyBodyweightRepository(
    SQLAlchemyBaseRepository[BodyweightLog, BodyweightLogTable], BodyweightRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BodyweightLogTable)

    async def list_by_date_range(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[BodyweightLog]:
        stmt = (
            select(BodyweightLogTable)
            .offset(offset)
            .limit(limit)
            .order_by(BodyweightLogTable.recorded_at.desc())
        )

        filters = []
        if date_from:
            filters.append(func.date(BodyweightLogTable.recorded_at) >= date_from)
        if date_to:
            filters.append(func.date(BodyweightLogTable.recorded_at) <= date_to)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def count_by_date_range(
        self, date_from: date | None = None, date_to: date | None = None
    ) -> int:
        stmt = select(func.count()).select_from(BodyweightLogTable)

        filters = []
        if date_from:
            filters.append(func.date(BodyweightLogTable.recorded_at) >= date_from)
        if date_to:
            filters.append(func.date(BodyweightLogTable.recorded_at) <= date_to)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    def _to_domain(self, model_obj: BodyweightLogTable) -> BodyweightLog:
        return BodyweightLog.model_validate(model_obj)

    def _to_model(self, entity: BodyweightLog) -> BodyweightLogTable:
        return BodyweightLogTable(
            id=entity.id,
            weight_kg=entity.weight_kg,
            recorded_at=entity.recorded_at,
            notes=entity.notes,
            created_at=entity.created_at,
        )

    def _update_model(self, model_obj: BodyweightLogTable, entity: BodyweightLog) -> None:
        model_obj.weight_kg = entity.weight_kg
        model_obj.recorded_at = entity.recorded_at
        model_obj.notes = entity.notes
