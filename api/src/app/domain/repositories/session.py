from collections.abc import Sequence
from datetime import date
from typing import Protocol
from uuid import UUID

from app.domain.entities.session import Session, SessionExercise, SessionSet
from app.domain.enums import SessionStatus
from app.domain.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session], Protocol):
    async def count_by_filters(
        self,
        status: SessionStatus | None = None,
        mesocycle_id: UUID | None = None,
        routine_id: UUID | None = None,
        exercise_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int: ...

    async def list_by_filters(
        self,
        status: SessionStatus | None = None,
        mesocycle_id: UUID | None = None,
        routine_id: UUID | None = None,
        exercise_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[Session]: ...

    async def get_by_date_range(self, start_date: date, end_date: date) -> Sequence[Session]: ...

    async def get_exercise_by_id(self, exercise_id: UUID) -> SessionExercise | None: ...

    async def add_exercise(
        self, session_id: UUID, session_exercise: SessionExercise
    ) -> SessionExercise: ...

    async def update_exercise(self, session_exercise: SessionExercise) -> SessionExercise: ...

    async def delete_exercise(self, exercise_id: UUID) -> None: ...

    async def get_set_by_id(self, set_id: UUID) -> SessionSet | None: ...

    async def add_set(self, session_exercise_id: UUID, session_set: SessionSet) -> SessionSet: ...

    async def update_set(self, session_set: SessionSet) -> SessionSet: ...

    async def delete_set(self, set_id: UUID) -> None: ...
