from collections.abc import Sequence
from datetime import date, datetime, time
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.session import Session, SessionExercise, SessionSet
from app.domain.enums import SessionStatus
from app.domain.repositories.session import SessionRepository
from app.infrastructure.database.models.exercise import ExerciseTable
from app.infrastructure.database.models.session import (
    SessionExerciseTable,
    SessionSetTable,
    SessionTable,
)
from app.infrastructure.database.repositories.base import SQLAlchemyBaseRepository


class SQLAlchemySessionRepository(
    SQLAlchemyBaseRepository[Session, SessionTable], SessionRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SessionTable)

    async def get_by_id(self, id: UUID) -> Session | None:
        stmt = (
            select(SessionTable)
            .where(SessionTable.id == id)
            .options(
                selectinload(SessionTable.session_exercises).selectinload(
                    SessionExerciseTable.session_sets
                ),
                selectinload(SessionTable.session_exercises)
                .selectinload(SessionExerciseTable.exercise)
                .selectinload(ExerciseTable.muscle_groups),
                selectinload(SessionTable.planned_session),
                selectinload(SessionTable.mesocycle),
                selectinload(SessionTable.routine),
            )
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            return self._to_domain(model_obj)
        return None

    async def list_by_filters(  # noqa: PLR0913
        self,
        status: SessionStatus | None = None,
        mesocycle_id: UUID | None = None,
        routine_id: UUID | None = None,
        exercise_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[Session]:
        stmt = (
            select(SessionTable)
            .offset(offset)
            .limit(limit)
            .order_by(SessionTable.started_at.desc())
            .options(
                selectinload(SessionTable.session_exercises).selectinload(
                    SessionExerciseTable.session_sets
                ),
                selectinload(SessionTable.session_exercises)
                .selectinload(SessionExerciseTable.exercise)
                .selectinload(ExerciseTable.muscle_groups),
            )
        )

        filters = []
        if status:
            filters.append(SessionTable.status == status)
        if mesocycle_id:
            filters.append(SessionTable.mesocycle_id == mesocycle_id)
        if routine_id:
            filters.append(SessionTable.routine_id == routine_id)
        if exercise_id:
            # We must join SessionExerciseTable to filter by exercise_id
            stmt = stmt.join(SessionTable.session_exercises).where(
                SessionExerciseTable.exercise_id == exercise_id
            )
        if date_from:
            dt_from = datetime.combine(date_from, time.min)
            filters.append(SessionTable.started_at >= dt_from)
        if date_to:
            dt_to = datetime.combine(date_to, time.max)
            filters.append(SessionTable.started_at <= dt_to)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await self._session.execute(stmt)
        # Use .unique() to handle the join results correctly with selectinload
        return [self._to_domain(row) for row in result.scalars().unique().all()]

    async def count_by_filters(  # noqa: PLR0913
        self,
        status: SessionStatus | None = None,
        mesocycle_id: UUID | None = None,
        routine_id: UUID | None = None,
        exercise_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        stmt = select(func.count(SessionTable.id)).select_from(SessionTable)

        filters = []
        if status:
            filters.append(SessionTable.status == status)
        if mesocycle_id:
            filters.append(SessionTable.mesocycle_id == mesocycle_id)
        if routine_id:
            filters.append(SessionTable.routine_id == routine_id)
        if exercise_id:
            # We must join SessionExerciseTable to filter by exercise_id
            stmt = stmt.join(SessionTable.session_exercises).where(
                SessionExerciseTable.exercise_id == exercise_id
            )
        if date_from:
            dt_from = datetime.combine(date_from, time.min)
            filters.append(SessionTable.started_at >= dt_from)
        if date_to:
            dt_to = datetime.combine(date_to, time.max)
            filters.append(SessionTable.started_at <= dt_to)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_by_date_range(self, start_date: date, end_date: date) -> Sequence[Session]:
        dt_start = datetime.combine(start_date, time.min)
        dt_end = datetime.combine(end_date, time.max)
        stmt = select(SessionTable).where(
            and_(
                SessionTable.started_at >= dt_start,
                SessionTable.started_at <= dt_end,
            )
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_exercise_by_id(self, exercise_id: UUID) -> SessionExercise | None:
        stmt = (
            select(SessionExerciseTable)
            .where(SessionExerciseTable.id == exercise_id)
            .options(
                selectinload(SessionExerciseTable.session_sets),
                selectinload(SessionExerciseTable.exercise).selectinload(
                    ExerciseTable.muscle_groups
                ),
            )
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            return self._to_exercise_domain(model_obj)
        return None

    async def add_exercise(
        self, session_id: UUID, session_exercise: SessionExercise
    ) -> SessionExercise:
        model = SessionExerciseTable(
            id=session_exercise.id,
            session_id=session_id,
            exercise_id=session_exercise.exercise.id,
            order=session_exercise.order,
            superset_group=session_exercise.superset_group,
            rest_seconds=session_exercise.rest_seconds,
            notes=session_exercise.notes,
        )
        self._session.add(model)
        await self._session.flush()

        # Return input for now, assuming success.
        # In a real scenario we might want to re-fetch to ensure DB state matches,
        # but here we trust the input entity structure.
        return session_exercise

    async def update_exercise(self, session_exercise: SessionExercise) -> SessionExercise:
        stmt = (
            select(SessionExerciseTable)
            .where(SessionExerciseTable.id == session_exercise.id)
            .options(
                selectinload(SessionExerciseTable.session_sets),
                selectinload(SessionExerciseTable.exercise).selectinload(
                    ExerciseTable.muscle_groups
                ),
            )
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()

        if not model_obj:
            raise ValueError(f"SessionExercise with id {session_exercise.id} not found")

        model_obj.order = session_exercise.order
        model_obj.superset_group = session_exercise.superset_group
        model_obj.rest_seconds = session_exercise.rest_seconds
        model_obj.notes = session_exercise.notes

        await self._session.flush()
        return self._to_exercise_domain(model_obj)

    async def delete_exercise(self, exercise_id: UUID) -> None:
        stmt = select(SessionExerciseTable).where(SessionExerciseTable.id == exercise_id)
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            await self._session.delete(model_obj)
            await self._session.flush()

    def _to_domain(self, model_obj: SessionTable) -> Session:
        exercises = []
        if (
            hasattr(model_obj, "__dict__")
            and "session_exercises" in model_obj.__dict__
            and model_obj.session_exercises is not None
        ):
            exercises = [self._to_exercise_domain(se) for se in model_obj.session_exercises]

        return Session(
            id=model_obj.id,
            planned_session_id=model_obj.planned_session_id,
            mesocycle_id=model_obj.mesocycle_id,
            routine_id=model_obj.routine_id,
            status=model_obj.status,
            started_at=model_obj.started_at,
            completed_at=model_obj.completed_at,
            notes=model_obj.notes,
            created_at=model_obj.created_at,
            updated_at=model_obj.updated_at,
            exercises=exercises,
        )

    def _to_exercise_domain(self, model_obj: SessionExerciseTable) -> SessionExercise:
        sets = []
        if (
            hasattr(model_obj, "__dict__")
            and "session_sets" in model_obj.__dict__
            and model_obj.session_sets is not None
        ):
            sets = [self._to_set_domain(ss) for ss in model_obj.session_sets]

        from app.domain.entities.exercise import Exercise, ExerciseMuscleGroup
        from app.domain.entities.muscle_group import MuscleGroup
        from app.domain.enums import MuscleRole

        exercise_domain = None
        if (
            hasattr(model_obj, "__dict__")
            and "exercise" in model_obj.__dict__
            and model_obj.exercise is not None
        ):
            mgs = []
            if (
                hasattr(model_obj.exercise, "__dict__")
                and "muscle_groups" in model_obj.exercise.__dict__
                and model_obj.exercise.muscle_groups is not None
            ):
                for mg_model in model_obj.exercise.muscle_groups:
                    mg = MuscleGroup(id=mg_model.id, name=mg_model.name)
                    mgs.append(
                        ExerciseMuscleGroup(
                            muscle_group=mg,
                            role=MuscleRole.PRIMARY,  # Default since role is in association table
                        )
                    )

            exercise_domain = Exercise(
                id=model_obj.exercise.id,
                name=model_obj.exercise.name,
                description=model_obj.exercise.description,
                equipment=model_obj.exercise.equipment,
                muscle_groups=mgs,
            )

        if exercise_domain is None:
            exercise_domain = Exercise(
                id=model_obj.exercise_id,
                name="Unknown Exercise",
                muscle_groups=[],
            )

        return SessionExercise(
            id=model_obj.id,
            exercise=exercise_domain,
            order=model_obj.order,
            superset_group=model_obj.superset_group,
            rest_seconds=model_obj.rest_seconds,
            notes=model_obj.notes,
            sets=sets,
        )

    def _to_set_domain(self, model_obj: SessionSetTable) -> SessionSet:
        return SessionSet(
            id=model_obj.id,
            set_number=model_obj.set_number,
            set_type=model_obj.set_type,
            target_reps=model_obj.target_reps,
            target_rir=model_obj.target_rir,
            target_weight_kg=model_obj.target_weight_kg,
            actual_reps=model_obj.actual_reps,
            actual_rir=model_obj.actual_rir,
            actual_weight_kg=model_obj.actual_weight_kg,
            weight_reduction_pct=model_obj.weight_reduction_pct,
            rest_seconds=model_obj.rest_seconds,
            performed_at=model_obj.performed_at,
        )

    def _to_model(self, entity: Session) -> SessionTable:
        model = SessionTable(
            id=entity.id,
            planned_session_id=entity.planned_session_id,
            mesocycle_id=entity.mesocycle_id,
            routine_id=entity.routine_id,
            status=entity.status,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

        for se_domain in entity.exercises:
            se_model = SessionExerciseTable(
                id=se_domain.id,
                session_id=entity.id,
                exercise_id=se_domain.exercise.id,
                order=se_domain.order,
                superset_group=se_domain.superset_group,
                rest_seconds=se_domain.rest_seconds,
                notes=se_domain.notes,
            )
            for ss_domain in se_domain.sets:
                ss_model = SessionSetTable(
                    id=ss_domain.id,
                    session_exercise_id=se_domain.id,
                    set_number=ss_domain.set_number,
                    set_type=ss_domain.set_type,
                    target_reps=ss_domain.target_reps,
                    target_rir=ss_domain.target_rir,
                    target_weight_kg=ss_domain.target_weight_kg,
                    actual_reps=ss_domain.actual_reps,
                    actual_rir=ss_domain.actual_rir,
                    actual_weight_kg=ss_domain.actual_weight_kg,
                    weight_reduction_pct=ss_domain.weight_reduction_pct,
                    rest_seconds=ss_domain.rest_seconds,
                    performed_at=ss_domain.performed_at,
                )
                se_model.session_sets.append(ss_model)
            model.session_exercises.append(se_model)

        return model

    def _update_model(self, model_obj: SessionTable, entity: Session) -> None:
        model_obj.status = entity.status
        model_obj.started_at = entity.started_at
        model_obj.completed_at = entity.completed_at
        model_obj.notes = entity.notes
        model_obj.updated_at = entity.updated_at

    async def get_set_by_id(self, set_id: UUID) -> SessionSet | None:
        stmt = select(SessionSetTable).where(SessionSetTable.id == set_id)
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            return self._to_set_domain(model_obj)
        return None

    async def add_set(self, session_exercise_id: UUID, session_set: SessionSet) -> SessionSet:
        model = SessionSetTable(
            id=session_set.id,
            session_exercise_id=session_exercise_id,
            set_number=session_set.set_number,
            set_type=session_set.set_type,
            target_reps=session_set.target_reps,
            target_rir=session_set.target_rir,
            target_weight_kg=session_set.target_weight_kg,
            weight_reduction_pct=session_set.weight_reduction_pct,
            rest_seconds=session_set.rest_seconds,
            performed_at=session_set.performed_at,
        )
        self._session.add(model)
        await self._session.flush()
        return session_set

    async def delete_set(self, set_id: UUID) -> None:
        stmt = select(SessionSetTable).where(SessionSetTable.id == set_id)
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            await self._session.delete(model_obj)
            await self._session.flush()

    async def update_set(self, session_set: SessionSet) -> SessionSet:
        stmt = select(SessionSetTable).where(SessionSetTable.id == session_set.id)
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()

        if not model_obj:
            raise ValueError(f"SessionSet with id {session_set.id} not found")

        model_obj.actual_reps = session_set.actual_reps
        model_obj.actual_rir = session_set.actual_rir
        model_obj.actual_weight_kg = session_set.actual_weight_kg
        model_obj.performed_at = session_set.performed_at

        # Ensure changes are flushed to the database
        await self._session.flush()
        return self._to_set_domain(model_obj)
