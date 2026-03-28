"""Session repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.session import Session, SessionSet


class SessionRepository(Protocol):
    """Persistence contract for workout sessions."""

    async def create(self, payload: dict[str, str | None]) -> Session:
        """Create one session."""
        ...

    async def start(self, session_id: str) -> Session:
        """Start one session."""
        ...

    async def complete(self, session_id: str) -> Session:
        """Complete one session."""
        ...

    async def log_set(
        self, set_id: str, payload: dict[str, int | float | str | None]
    ) -> SessionSet:
        """Log actual set performance."""
        ...
