"""Session application service."""

from __future__ import annotations

from workouter_cli.domain.entities.session import Session, SessionSet
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

    async def log_set(
        self, set_id: str, payload: dict[str, int | float | str | None]
    ) -> SessionSet:
        return await self.session_repository.log_set(set_id, payload)
