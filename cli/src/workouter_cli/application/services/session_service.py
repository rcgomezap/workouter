"""Session application service."""

from __future__ import annotations

from workouter_cli.domain.entities.session import Session, SessionExercise, SessionSet
from workouter_cli.domain.repositories.session import SessionRepository


class SessionService:
    """Session use-cases orchestration and business defaults."""

    def __init__(self, session_repository: SessionRepository) -> None:
        self.session_repository = session_repository

    async def create(self, payload: dict[str, str | None]) -> Session:
        return await self.session_repository.create(payload)

    async def start(self, session_id: str) -> Session:
        return await self.session_repository.start(session_id)

    async def complete(self, session_id: str) -> Session:
        return await self.session_repository.complete(session_id)

    async def update(self, session_id: str, payload: dict[str, str | None]) -> Session:
        return await self.session_repository.update(session_id, payload)

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        mesocycle_id: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[Session], dict[str, int]]:
        return await self.session_repository.list(
            page=page,
            page_size=page_size,
            status=status,
            mesocycle_id=mesocycle_id,
            date_from=date_from,
            date_to=date_to,
        )

    async def get(self, session_id: str) -> Session:
        return await self.session_repository.get(session_id)

    async def delete(self, session_id: str) -> bool:
        return await self.session_repository.delete(session_id)

    async def add_exercise(self, session_id: str, payload: dict[str, object]) -> Session:
        return await self.session_repository.add_exercise(session_id, payload)

    async def update_exercise(
        self, session_exercise_id: str, payload: dict[str, object]
    ) -> SessionExercise:
        return await self.session_repository.update_exercise(session_exercise_id, payload)

    async def remove_exercise(self, session_exercise_id: str) -> bool:
        return await self.session_repository.remove_exercise(session_exercise_id)

    async def add_set(
        self, session_exercise_id: str, payload: dict[str, object]
    ) -> SessionExercise:
        return await self.session_repository.add_set(session_exercise_id, payload)

    async def update_set(self, set_id: str, payload: dict[str, object]) -> SessionSet:
        return await self.session_repository.update_set(set_id, payload)

    async def remove_set(self, set_id: str) -> bool:
        return await self.session_repository.remove_set(set_id)

    async def log_set(
        self, set_id: str, payload: dict[str, int | float | str | None]
    ) -> SessionSet:
        return await self.session_repository.log_set(set_id, payload)
