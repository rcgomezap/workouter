from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.unit_of_work import UnitOfWork
from app.infrastructure.database.repositories.bodyweight import SQLAlchemyBodyweightRepository
from app.infrastructure.database.repositories.exercise import SQLAlchemyExerciseRepository
from app.infrastructure.database.repositories.mesocycle import SQLAlchemyMesocycleRepository
from app.infrastructure.database.repositories.muscle_group import SQLAlchemyMuscleGroupRepository
from app.infrastructure.database.repositories.routine import SQLAlchemyRoutineRepository
from app.infrastructure.database.repositories.session import SQLAlchemySessionRepository


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session
        self.exercise_repository = SQLAlchemyExerciseRepository(session)
        self.muscle_group_repository = SQLAlchemyMuscleGroupRepository(session)
        self.routine_repository = SQLAlchemyRoutineRepository(session)
        self.mesocycle_repository = SQLAlchemyMesocycleRepository(session)
        self.session_repository = SQLAlchemySessionRepository(session)
        self.bodyweight_repository = SQLAlchemyBodyweightRepository(session)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def flush(self) -> None:
        await self._session.flush()
