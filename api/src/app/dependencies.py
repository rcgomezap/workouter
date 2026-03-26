from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.backup_service import BackupService
from app.application.services.bodyweight_service import BodyweightService
from app.application.services.calendar_service import CalendarService
from app.application.services.exercise_service import ExerciseService
from app.application.services.insight_service import InsightService
from app.application.services.mesocycle_service import MesocycleService
from app.application.services.muscle_group_service import MuscleGroupService
from app.application.services.routine_service import RoutineService
from app.application.services.session_service import SessionService
from app.infrastructure.database.connection import get_session_factory
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session


async def get_unit_of_work(session: AsyncSession = Depends(get_db_session)) -> UnitOfWork:
    return SQLAlchemyUnitOfWork(session)


async def get_exercise_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> ExerciseService:
    return ExerciseService(uow)


async def get_muscle_group_service(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> MuscleGroupService:
    return MuscleGroupService(uow)


async def get_routine_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> RoutineService:
    return RoutineService(uow)


async def get_mesocycle_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> MesocycleService:
    return MesocycleService(uow)


async def get_session_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> SessionService:
    return SessionService(uow)


async def get_bodyweight_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> BodyweightService:
    return BodyweightService(uow)


async def get_insight_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> InsightService:
    return InsightService(uow)


async def get_calendar_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> CalendarService:
    return CalendarService(uow)


async def get_backup_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> BackupService:
    from app.config.loader import load_config
    from app.infrastructure.backup.manager import BackupManager
    from app.infrastructure.database.connection import get_engine

    return BackupManager(load_config(), get_engine())
