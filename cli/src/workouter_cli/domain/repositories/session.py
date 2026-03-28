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

    async def update(self, session_id: str, payload: dict[str, str | None]) -> Session:
        """Update one session."""
        ...

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Session], dict[str, int]]:
        """List sessions and return items with pagination metadata."""
        ...

    async def log_set(
        self, set_id: str, payload: dict[str, int | float | str | None]
    ) -> SessionSet:
        """Log actual set performance."""
        ...
