from typing import Protocol, Self
from app.domain.repositories.exercise import ExerciseRepository
from app.domain.repositories.muscle_group import MuscleGroupRepository
from app.domain.repositories.routine import RoutineRepository
from app.domain.repositories.mesocycle import MesocycleRepository
from app.domain.repositories.session import SessionRepository
from app.domain.repositories.bodyweight import BodyweightRepository


class UnitOfWork(Protocol):
    exercise_repository: ExerciseRepository
    muscle_group_repository: MuscleGroupRepository
    routine_repository: RoutineRepository
    mesocycle_repository: MesocycleRepository
    session_repository: SessionRepository
    bodyweight_repository: BodyweightRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def flush(self) -> None: ...
