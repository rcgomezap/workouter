from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, func, insert, select
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.base import NO_VALUE

from app.domain.entities.exercise import Exercise, ExerciseMuscleGroup
from app.domain.entities.muscle_group import MuscleGroup
from app.domain.enums import MuscleRole
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
            roles_by_muscle_group = await self._get_roles_by_muscle_group(id)
            return self._to_domain_with_roles(model_obj, roles_by_muscle_group)
        return None

    async def list(self, offset: int = 0, limit: int = 20) -> Sequence[Exercise]:
        stmt = (
            select(ExerciseTable)
            .offset(offset)
            .limit(limit)
            .options(selectinload(ExerciseTable.muscle_groups))
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        roles_by_exercise = await self._get_roles_by_exercise([m.id for m in models])
        return [
            self._to_domain_with_roles(row, roles_by_exercise.get(row.id, {})) for row in models
        ]

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
        models = result.scalars().all()
        roles_by_exercise = await self._get_roles_by_exercise([m.id for m in models])
        return [
            self._to_domain_with_roles(row, roles_by_exercise.get(row.id, {})) for row in models
        ]

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
        refreshed = await self.get_by_id(entity.id)
        if refreshed is None:
            raise ValueError(f"Entity with id {entity.id} not found")
        return refreshed

    async def _get_roles_by_exercise(
        self, exercise_ids: list[UUID]
    ) -> dict[UUID, dict[UUID, MuscleRole]]:
        if not exercise_ids:
            return {}

        stmt = select(
            exercise_muscle_group.c.exercise_id,
            exercise_muscle_group.c.muscle_group_id,
            exercise_muscle_group.c.role,
        ).where(exercise_muscle_group.c.exercise_id.in_(exercise_ids))

        result = await self._session.execute(stmt)
        roles_by_exercise: dict[UUID, dict[UUID, MuscleRole]] = {}

        for exercise_id, muscle_group_id, role in result.all():
            roles_by_exercise.setdefault(exercise_id, {})[muscle_group_id] = MuscleRole(role)

        return roles_by_exercise

    async def _get_roles_by_muscle_group(self, exercise_id: UUID) -> dict[UUID, MuscleRole]:
        roles_by_exercise = await self._get_roles_by_exercise([exercise_id])
        return roles_by_exercise.get(exercise_id, {})

    def _to_domain_with_roles(
        self,
        model_obj: ExerciseTable,
        roles_by_muscle_group: dict[UUID, MuscleRole],
    ) -> Exercise:
        muscle_groups = [
            ExerciseMuscleGroup(muscle_group=MuscleGroup.model_validate(mg), role=role)
            for mg in model_obj.muscle_groups
            if (role := roles_by_muscle_group.get(mg.id)) is not None
        ]

        return Exercise(
            id=model_obj.id,
            name=model_obj.name,
            description=model_obj.description,
            equipment=model_obj.equipment,
            created_at=model_obj.created_at,
            updated_at=model_obj.updated_at,
            muscle_groups=muscle_groups,
        )

    def _to_domain(self, model_obj: ExerciseTable) -> Exercise:
        muscle_groups: list[ExerciseMuscleGroup] | None = None
        inspection = sa_inspect(model_obj)
        if inspection.attrs.muscle_groups.loaded_value is not NO_VALUE:
            muscle_groups = []

        return Exercise(
            id=model_obj.id,
            name=model_obj.name,
            description=model_obj.description,
            equipment=model_obj.equipment,
            created_at=model_obj.created_at,
            updated_at=model_obj.updated_at,
            muscle_groups=muscle_groups,
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
