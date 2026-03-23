from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.domain.entities.routine import Routine
from app.domain.repositories.routine import RoutineRepository
from app.infrastructure.database.models.routine import RoutineTable, RoutineExerciseTable, RoutineSetTable
from app.infrastructure.database.repositories.base import SQLAlchemyBaseRepository


class SQLAlchemyRoutineRepository(
    SQLAlchemyBaseRepository[Routine, RoutineTable], RoutineRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RoutineTable)

    async def get_by_id(self, id: UUID) -> Routine | None:
        stmt = (
            select(RoutineTable)
            .where(RoutineTable.id == id)
            .options(
                selectinload(RoutineTable.routine_exercises).selectinload(
                    RoutineExerciseTable.routine_sets
                ),
                selectinload(RoutineTable.routine_exercises).selectinload(
                    RoutineExerciseTable.exercise
                ),
            )
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            return self._to_domain(model_obj)
        return None

    async def count_total(self) -> int:
        stmt = select(func.count()).select_from(RoutineTable)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    def _to_domain(self, model_obj: RoutineTable) -> Routine:
        return Routine.model_validate(model_obj)

    def _to_model(self, entity: Routine) -> RoutineTable:
        return RoutineTable(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _update_model(self, model_obj: RoutineTable, entity: Routine) -> None:
        model_obj.name = entity.name
        model_obj.description = entity.description
        model_obj.updated_at = entity.updated_at
