from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.muscle_group import MuscleGroup
from app.domain.repositories.muscle_group import MuscleGroupRepository
from app.infrastructure.database.models.muscle_group import MuscleGroupTable
from app.infrastructure.database.repositories.base import SQLAlchemyBaseRepository


class SQLAlchemyMuscleGroupRepository(
    SQLAlchemyBaseRepository[MuscleGroup, MuscleGroupTable], MuscleGroupRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MuscleGroupTable)

    async def get_by_name(self, name: str) -> MuscleGroup | None:
        stmt = select(MuscleGroupTable).where(MuscleGroupTable.name == name)
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            return self._to_domain(model_obj)
        return None

    async def list_all(self) -> Sequence[MuscleGroup]:
        stmt = select(MuscleGroupTable).order_by(MuscleGroupTable.name)
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    def _to_domain(self, model_obj: MuscleGroupTable) -> MuscleGroup:
        return MuscleGroup.model_validate(model_obj)

    def _to_model(self, entity: MuscleGroup) -> MuscleGroupTable:
        return MuscleGroupTable(
            id=entity.id,
            name=entity.name,
        )

    def _update_model(self, model_obj: MuscleGroupTable, entity: MuscleGroup) -> None:
        model_obj.name = entity.name
