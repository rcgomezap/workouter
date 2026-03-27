from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.exercise import Exercise
from app.domain.repositories.exercise import ExerciseRepository
from app.infrastructure.database.models.exercise import ExerciseTable, exercise_muscle_group
from app.infrastructure.database.repositories.base import SQLAlchemyBaseRepository


class SQLAlchemyExerciseRepository(
    SQLAlchemyBaseRepository[Exercise, ExerciseTable], ExerciseRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ExerciseTable)

    async def get_by_id(self, id: UUID) -> Exercise | None:
        stmt = (
            select(ExerciseTable)
            .where(ExerciseTable.id == id)
            .options(selectinload(ExerciseTable.muscle_groups))
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            return self._to_domain(model_obj)
        return None

    async def list(self, offset: int = 0, limit: int = 20) -> Sequence[Exercise]:
        stmt = (
            select(ExerciseTable)
            .offset(offset)
            .limit(limit)
            .options(selectinload(ExerciseTable.muscle_groups))
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def list_by_muscle_group(
        self, muscle_group_id: UUID, offset: int = 0, limit: int = 20
    ) -> Sequence[Exercise]:
        stmt = (
            select(ExerciseTable)
            .join(exercise_muscle_group)
            .where(exercise_muscle_group.c.muscle_group_id == muscle_group_id)
            .offset(offset)
            .limit(limit)
            .options(selectinload(ExerciseTable.muscle_groups))
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def count_by_muscle_group(self, muscle_group_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(exercise_muscle_group)
            .where(exercise_muscle_group.c.muscle_group_id == muscle_group_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def count_total(self) -> int:
        stmt = select(func.count()).select_from(ExerciseTable)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def update(self, entity: Exercise) -> Exercise:
        stmt = (
            select(ExerciseTable)
            .where(ExerciseTable.id == entity.id)
            .options(selectinload(ExerciseTable.muscle_groups))
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()

        if not model_obj:
            raise ValueError(f"Entity with id {entity.id} not found")

        self._update_model(model_obj, entity)

        if entity.muscle_groups is not None:
            await self._session.execute(
                delete(exercise_muscle_group).where(
                    exercise_muscle_group.c.exercise_id == entity.id
                )
            )

            if entity.muscle_groups:
                await self._session.execute(
                    insert(exercise_muscle_group),
                    [
                        {
                            "exercise_id": entity.id,
                            "muscle_group_id": mg.muscle_group.id,
                            "role": mg.role,
                        }
                        for mg in entity.muscle_groups
                    ],
                )

        await self._session.flush()
        await self._session.refresh(model_obj)
        return self._to_domain(model_obj)

    def _to_domain(self, model_obj: ExerciseTable) -> Exercise:
        # Note: In a real implementation, you'd handle the role from the association table
        # This requires more complex querying or mapping.
        # For now, simplifying by ignoring muscle_groups if they are not loaded
        # to avoid MissingGreenlet errors during Pydantic validation.
        return Exercise(
            id=model_obj.id,
            name=model_obj.name,
            description=model_obj.description,
            equipment=model_obj.equipment,
            created_at=model_obj.created_at,
            updated_at=model_obj.updated_at,
            muscle_groups=None,
        )

    def _to_model(self, entity: Exercise) -> ExerciseTable:
        return ExerciseTable(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            equipment=entity.equipment,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _update_model(self, model_obj: ExerciseTable, entity: Exercise) -> None:
        model_obj.name = entity.name
        model_obj.description = entity.description
        model_obj.equipment = entity.equipment
        model_obj.updated_at = entity.updated_at
