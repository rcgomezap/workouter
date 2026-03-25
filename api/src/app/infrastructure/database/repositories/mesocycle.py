from typing import Sequence
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.domain.entities.mesocycle import Mesocycle, MesocycleWeek, PlannedSession
from app.domain.enums import MesocycleStatus, WeekType
from app.domain.repositories.mesocycle import MesocycleRepository
from app.infrastructure.database.models.mesocycle import MesocycleTable, MesocycleWeekTable
from app.infrastructure.database.models.session import PlannedSessionTable
from app.infrastructure.database.models.routine import RoutineTable, RoutineExerciseTable
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
                selectinload(MesocycleTable.weeks)
                .selectinload(MesocycleWeekTable.planned_sessions)
                .selectinload(PlannedSessionTable.routine)
                .selectinload(RoutineTable.routine_exercises)
                .selectinload(RoutineExerciseTable.routine_sets),
                selectinload(MesocycleTable.weeks)
                .selectinload(MesocycleWeekTable.planned_sessions)
                .selectinload(PlannedSessionTable.routine)
                .selectinload(RoutineTable.routine_exercises)
                .selectinload(RoutineExerciseTable.exercise),
            )
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            return self._to_domain(model_obj)
        return None

    async def get_week_by_id(self, week_id: UUID) -> MesocycleWeek | None:
        stmt = (
            select(MesocycleWeekTable)
            .where(MesocycleWeekTable.id == week_id)
            .options(
                selectinload(MesocycleWeekTable.planned_sessions)
                .selectinload(PlannedSessionTable.routine)
                .selectinload(RoutineTable.routine_exercises)
                .selectinload(RoutineExerciseTable.routine_sets),
                selectinload(MesocycleWeekTable.planned_sessions)
                .selectinload(PlannedSessionTable.routine)
                .selectinload(RoutineTable.routine_exercises)
                .selectinload(RoutineExerciseTable.exercise),
            )
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            return self._to_week_domain(model_obj)
        return None

    async def get_planned_session_by_id(self, ps_id: UUID) -> PlannedSession | None:
        stmt = (
            select(PlannedSessionTable)
            .where(PlannedSessionTable.id == ps_id)
            .options(
                selectinload(PlannedSessionTable.routine)
                .selectinload(RoutineTable.routine_exercises)
                .selectinload(RoutineExerciseTable.routine_sets),
                selectinload(PlannedSessionTable.routine)
                .selectinload(RoutineTable.routine_exercises)
                .selectinload(RoutineExerciseTable.exercise),
            )
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            return self._to_planned_session_domain(model_obj)
        return None

    async def get_planned_sessions_by_date_range(
        self, start_date: date, end_date: date
    ) -> Sequence[PlannedSession]:
        stmt = (
            select(PlannedSessionTable)
            .where(PlannedSessionTable.date >= start_date, PlannedSessionTable.date <= end_date)
            .options(
                selectinload(PlannedSessionTable.routine)
                .selectinload(RoutineTable.routine_exercises)
                .selectinload(RoutineExerciseTable.routine_sets),
                selectinload(PlannedSessionTable.routine)
                .selectinload(RoutineTable.routine_exercises)
                .selectinload(RoutineExerciseTable.exercise),
            )
        )
        result = await self._session.execute(stmt)
        return [self._to_planned_session_domain(row) for row in result.scalars().all()]

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
        stmt = (
            select(func.count()).select_from(MesocycleTable).where(MesocycleTable.status == status)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def count_total(self) -> int:
        stmt = select(func.count()).select_from(MesocycleTable)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def update(self, entity: Mesocycle) -> Mesocycle:
        stmt = (
            select(MesocycleTable)
            .where(MesocycleTable.id == entity.id)
            .options(
                selectinload(MesocycleTable.weeks).selectinload(MesocycleWeekTable.planned_sessions)
            )
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()

        if not model_obj:
            raise ValueError(f"Mesocycle with id {entity.id} not found")

        self._update_model(model_obj, entity)
        await self._session.flush()
        # We don't necessarily need refresh if we are returning domain from the updated model
        return self._to_domain(model_obj)

    def _to_domain(self, model_obj: MesocycleTable) -> Mesocycle:
        # Avoid lazy loading issues during validation by checking if relationships are loaded
        weeks = []
        try:
            # Check if 'weeks' is in __dict__ to see if it was loaded via selectinload
            if "weeks" in model_obj.__dict__:
                weeks = [self._to_week_domain(week) for week in model_obj.weeks]
        except Exception:
            pass

        return Mesocycle(
            id=model_obj.id,
            name=model_obj.name,
            description=model_obj.description,
            start_date=model_obj.start_date,
            end_date=model_obj.end_date,
            status=model_obj.status,
            created_at=model_obj.created_at,
            updated_at=model_obj.updated_at,
            weeks=weeks,
        )

    def _to_week_domain(self, model_obj: MesocycleWeekTable) -> MesocycleWeek:
        planned_sessions = []
        try:
            if "planned_sessions" in model_obj.__dict__:
                planned_sessions = [
                    self._to_planned_session_domain(ps) for ps in model_obj.planned_sessions
                ]
        except Exception:
            pass

        return MesocycleWeek(
            id=model_obj.id,
            mesocycle_id=model_obj.mesocycle_id,
            week_number=model_obj.week_number,
            week_type=model_obj.week_type,
            start_date=model_obj.start_date,
            end_date=model_obj.end_date,
            planned_sessions=planned_sessions,
        )

    def _to_planned_session_domain(self, model_obj: PlannedSessionTable) -> PlannedSession:
        routine = None
        try:
            if "routine" in model_obj.__dict__ and model_obj.routine:
                from app.infrastructure.database.repositories.routine import (
                    SQLAlchemyRoutineRepository,
                )

                # Create a temporary repository to use its _to_domain logic
                # This is safe as long as we don't call async methods on it
                routine_repo = SQLAlchemyRoutineRepository(self._session)
                routine = routine_repo._to_domain(model_obj.routine)
        except Exception:
            pass

        return PlannedSession(
            id=model_obj.id,
            mesocycle_week_id=model_obj.mesocycle_week_id,
            day_of_week=model_obj.day_of_week,
            date=model_obj.date,
            notes=model_obj.notes,
            routine=routine,
        )

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

        # Synchronize weeks
        weeks_to_check = []
        if "weeks" in model_obj.__dict__:
            weeks_to_check = model_obj.weeks
        else:
            model_obj.weeks = []
            weeks_to_check = []

        existing_week_ids = {w.id for w in weeks_to_check}
        domain_week_ids = {w.id for w in entity.weeks}

        # Remove weeks
        model_obj.weeks = [w for w in model_obj.weeks if w.id in domain_week_ids]

        # Add or update weeks
        for week_domain in entity.weeks:
            if week_domain.id not in existing_week_ids:
                week_model = MesocycleWeekTable(
                    id=week_domain.id,
                    mesocycle_id=entity.id,
                    week_number=week_domain.week_number,
                    week_type=week_domain.week_type,
                    start_date=week_domain.start_date,
                    end_date=week_domain.end_date,
                )
                model_obj.weeks.append(week_model)
            else:
                # Update existing week
                week_model = next(w for w in weeks_to_check if w.id == week_domain.id)
                week_model.week_number = week_domain.week_number
                week_model.week_type = week_domain.week_type
                week_model.start_date = week_domain.start_date
                week_model.end_date = week_domain.end_date

            # Synchronize planned sessions for this week
            ps_to_check = []
            if "planned_sessions" in week_model.__dict__:
                ps_to_check = week_model.planned_sessions
            else:
                week_model.planned_sessions = []
                ps_to_check = []

            existing_ps_ids = {ps.id for ps in ps_to_check}
            domain_ps_ids = {ps.id for ps in week_domain.planned_sessions}

            # Remove planned sessions
            week_model.planned_sessions = [
                ps for ps in week_model.planned_sessions if ps.id in domain_ps_ids
            ]

            # Add or update planned sessions
            for ps_domain in week_domain.planned_sessions:
                if ps_domain.id not in existing_ps_ids:
                    ps_model = PlannedSessionTable(
                        id=ps_domain.id,
                        mesocycle_week_id=week_domain.id,
                        routine_id=ps_domain.routine.id if ps_domain.routine else None,
                        day_of_week=ps_domain.day_of_week,
                        date=ps_domain.date,
                        notes=ps_domain.notes,
                    )
                    week_model.planned_sessions.append(ps_model)
                else:
                    ps_model = next(ps for ps in ps_to_check if ps.id == ps_domain.id)
                    ps_model.routine_id = ps_domain.routine.id if ps_domain.routine else None
                    ps_model.day_of_week = ps_domain.day_of_week
                    ps_model.date = ps_domain.date
                    ps_model.notes = ps_domain.notes
