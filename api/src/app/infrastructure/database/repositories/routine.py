from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.domain.entities.routine import Routine, RoutineExercise, RoutineSet
from app.domain.repositories.routine import RoutineRepository
from app.infrastructure.database.models.routine import (
    RoutineTable,
    RoutineExerciseTable,
    RoutineSetTable,
)
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

    async def get_exercise_by_id(self, id: UUID) -> RoutineExercise | None:
        stmt = (
            select(RoutineExerciseTable)
            .where(RoutineExerciseTable.id == id)
            .options(
                selectinload(RoutineExerciseTable.routine_sets),
                selectinload(RoutineExerciseTable.exercise),
            )
        )
        result = await self._session.execute(stmt)
        re_model = result.scalar_one_or_none()
        if re_model:
            # We need to map to domain. Since RoutineExercise needs an Exercise domain entity,
            # we can reuse the logic from _to_domain or just map it here.
            from app.domain.entities.exercise import Exercise

            exercise = Exercise(
                id=re_model.exercise.id,
                name=re_model.exercise.name,
                description=re_model.exercise.description,
                equipment=re_model.exercise.equipment,
                muscle_groups=[],
            )
            sets = [
                RoutineSet(
                    id=rs.id,
                    routine_exercise_id=rs.routine_exercise_id,
                    set_number=rs.set_number,
                    set_type=rs.set_type,
                    target_reps_min=rs.target_reps_min,
                    target_reps_max=rs.target_reps_max,
                    target_rir=rs.target_rir,
                    target_weight_kg=rs.target_weight_kg,
                    weight_reduction_pct=rs.weight_reduction_pct,
                    rest_seconds=rs.rest_seconds,
                )
                for rs in re_model.routine_sets
            ]
            re_domain = RoutineExercise(
                id=re_model.id,
                routine_id=re_model.routine_id,
                exercise=exercise,
                order=re_model.order,
                superset_group=re_model.superset_group,
                rest_seconds=re_model.rest_seconds,
                notes=re_model.notes,
                sets=sets,
            )
            return re_domain
        return None

    async def delete_exercise(self, id: UUID) -> bool:
        stmt = select(RoutineExerciseTable).where(RoutineExerciseTable.id == id)
        result = await self._session.execute(stmt)
        re_model = result.scalar_one_or_none()
        if re_model:
            await self._session.delete(re_model)
            await self._session.flush()
            return True
        return False

    async def get_set_by_id(self, id: UUID) -> RoutineSet | None:
        stmt = select(RoutineSetTable).where(RoutineSetTable.id == id)
        result = await self._session.execute(stmt)
        rs_model = result.scalar_one_or_none()
        if rs_model:
            rs_domain = RoutineSet(
                id=rs_model.id,
                routine_exercise_id=rs_model.routine_exercise_id,
                set_number=rs_model.set_number,
                set_type=rs_model.set_type,
                target_reps_min=rs_model.target_reps_min,
                target_reps_max=rs_model.target_reps_max,
                target_rir=rs_model.target_rir,
                target_weight_kg=rs_model.target_weight_kg,
                weight_reduction_pct=rs_model.weight_reduction_pct,
                rest_seconds=rs_model.rest_seconds,
            )
            return rs_domain
        return None

    async def delete_set(self, id: UUID) -> bool:
        stmt = select(RoutineSetTable).where(RoutineSetTable.id == id)
        result = await self._session.execute(stmt)
        rs_model = result.scalar_one_or_none()
        if rs_model:
            await self._session.delete(rs_model)
            await self._session.flush()
            return True
        return False

    def _to_domain(self, model_obj: RoutineTable) -> Routine:
        exercises = []
        # Check __dict__ to avoid triggering lazy loads
        if "routine_exercises" in model_obj.__dict__:
            for re_model in model_obj.routine_exercises:
                sets = []
                if "routine_sets" in re_model.__dict__:
                    for rs_model in re_model.routine_sets:
                        sets.append(
                            RoutineSet(
                                id=rs_model.id,
                                routine_exercise_id=rs_model.routine_exercise_id,
                                set_number=rs_model.set_number,
                                set_type=rs_model.set_type,
                                target_reps_min=rs_model.target_reps_min,
                                target_reps_max=rs_model.target_reps_max,
                                target_rir=rs_model.target_rir,
                                target_weight_kg=rs_model.target_weight_kg,
                                weight_reduction_pct=rs_model.weight_reduction_pct,
                                rest_seconds=rs_model.rest_seconds,
                            )
                        )

                exercise = None
                if "exercise" in re_model.__dict__ and re_model.exercise is not None:
                    from app.domain.entities.exercise import Exercise

                    exercise = Exercise(
                        id=re_model.exercise.id,
                        name=re_model.exercise.name,
                        description=re_model.exercise.description,
                        equipment=re_model.exercise.equipment,
                        muscle_groups=[],
                    )

                if exercise is None:
                    from app.domain.entities.exercise import Exercise

                    exercise = Exercise(
                        id=re_model.exercise_id,
                        name="Unknown Exercise",
                        muscle_groups=[],
                    )

                exercises.append(
                    RoutineExercise(
                        id=re_model.id,
                        routine_id=re_model.routine_id,
                        exercise=exercise,
                        order=re_model.order,
                        superset_group=re_model.superset_group,
                        rest_seconds=re_model.rest_seconds,
                        notes=re_model.notes,
                        sets=sets,
                    )
                )

        return Routine(
            id=model_obj.id,
            name=model_obj.name,
            description=model_obj.description,
            created_at=model_obj.created_at,
            updated_at=model_obj.updated_at,
            exercises=exercises,
        )

    async def add(self, entity: Routine) -> Routine:
        model_obj = self._to_model(entity)
        self._session.add(model_obj)
        await self._session.flush()
        # Re-fetch with all options to ensure _to_domain has everything
        stmt = (
            select(RoutineTable)
            .where(RoutineTable.id == entity.id)
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
        refetched = result.scalar_one()
        return self._to_domain(refetched)

    async def update(self, entity: Routine) -> Routine:
        stmt = (
            select(RoutineTable)
            .where(RoutineTable.id == entity.id)
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

        if not model_obj:
            raise ValueError(f"Routine with id {entity.id} not found")

        self._update_model(model_obj, entity)
        await self._session.flush()
        return self._to_domain(model_obj)

    def _to_model(self, entity: Routine) -> RoutineTable:
        model = RoutineTable(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        for re_domain in entity.exercises:
            re_model = RoutineExerciseTable(
                id=re_domain.id,
                routine_id=entity.id,
                exercise_id=re_domain.exercise.id,
                order=re_domain.order,
                superset_group=re_domain.superset_group,
                rest_seconds=re_domain.rest_seconds,
                notes=re_domain.notes,
            )
            # Ensure routine_sets is initialized
            re_model.routine_sets = []
            for rs_domain in re_domain.sets:
                rs_model = RoutineSetTable(
                    id=rs_domain.id,
                    routine_exercise_id=re_domain.id,
                    set_number=rs_domain.set_number,
                    set_type=rs_domain.set_type,
                    target_reps_min=rs_domain.target_reps_min,
                    target_reps_max=rs_domain.target_reps_max,
                    target_rir=rs_domain.target_rir,
                    target_weight_kg=rs_domain.target_weight_kg,
                    weight_reduction_pct=rs_domain.weight_reduction_pct,
                    rest_seconds=rs_domain.rest_seconds,
                )
                re_model.routine_sets.append(rs_model)
            model.routine_exercises.append(re_model)
        return model

    def _update_model(self, model_obj: RoutineTable, entity: Routine) -> None:
        model_obj.name = entity.name
        model_obj.description = entity.description
        model_obj.updated_at = entity.updated_at

        # Synchronize exercises
        if "routine_exercises" in model_obj.__dict__:
            existing_re_ids = {re.id for re in model_obj.routine_exercises}
            domain_re_ids = {re.id for re in entity.exercises}

            # Remove exercises
            model_obj.routine_exercises = [
                re for re in model_obj.routine_exercises if re.id in domain_re_ids
            ]

            # Add or update exercises
            for re_domain in entity.exercises:
                if re_domain.id not in existing_re_ids:
                    re_model = RoutineExerciseTable(
                        id=re_domain.id,
                        routine_id=entity.id,
                        exercise_id=re_domain.exercise.id,
                        order=re_domain.order,
                        superset_group=re_domain.superset_group,
                        rest_seconds=re_domain.rest_seconds,
                        notes=re_domain.notes,
                    )
                    # Initialize sets for the new exercise
                    re_model.routine_sets = []
                    for rs_domain in re_domain.sets:
                        rs_model = RoutineSetTable(
                            id=rs_domain.id,
                            routine_exercise_id=re_domain.id,
                            set_number=rs_domain.set_number,
                            set_type=rs_domain.set_type,
                            target_reps_min=rs_domain.target_reps_min,
                            target_reps_max=rs_domain.target_reps_max,
                            target_rir=rs_domain.target_rir,
                            target_weight_kg=rs_domain.target_weight_kg,
                            weight_reduction_pct=rs_domain.weight_reduction_pct,
                            rest_seconds=rs_domain.rest_seconds,
                        )
                        re_model.routine_sets.append(rs_model)
                    model_obj.routine_exercises.append(re_model)
                else:
                    re_model = next(
                        re for re in model_obj.routine_exercises if re.id == re_domain.id
                    )
                    re_model.order = re_domain.order
                    re_model.superset_group = re_domain.superset_group
                    re_model.rest_seconds = re_domain.rest_seconds
                    re_model.notes = re_domain.notes

                    # Synchronize sets for this exercise
                    if "routine_sets" not in re_model.__dict__:
                        re_model.routine_sets = []
                    existing_rs_ids = {rs.id for rs in re_model.routine_sets}

                    domain_rs_ids = {rs.id for rs in re_domain.sets}

                    # Remove sets
                    re_model.routine_sets = [
                        rs for rs in re_model.routine_sets if rs.id in domain_rs_ids
                    ]

                    # Add or update sets
                    for rs_domain in re_domain.sets:
                        if rs_domain.id not in existing_rs_ids:
                            rs_model = RoutineSetTable(
                                id=rs_domain.id,
                                routine_exercise_id=re_domain.id,
                                set_number=rs_domain.set_number,
                                set_type=rs_domain.set_type,
                                target_reps_min=rs_domain.target_reps_min,
                                target_reps_max=rs_domain.target_reps_max,
                                target_rir=rs_domain.target_rir,
                                target_weight_kg=rs_domain.target_weight_kg,
                                weight_reduction_pct=rs_domain.weight_reduction_pct,
                                rest_seconds=rs_domain.rest_seconds,
                            )
                            re_model.routine_sets.append(rs_model)
                        else:
                            rs_model = next(
                                rs for rs in re_model.routine_sets if rs.id == rs_domain.id
                            )
                            rs_model.set_number = rs_domain.set_number
                            rs_model.set_type = rs_domain.set_type
                            rs_model.target_reps_min = rs_domain.target_reps_min
                            rs_model.target_reps_max = rs_domain.target_reps_max
                            rs_model.target_rir = rs_domain.target_rir
                            rs_model.target_weight_kg = rs_domain.target_weight_kg
                            rs_model.weight_reduction_pct = rs_domain.weight_reduction_pct
                            rs_model.rest_seconds = rs_domain.rest_seconds
