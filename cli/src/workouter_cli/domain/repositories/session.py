"""Session repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.session import Session, SessionExercise, SessionSet


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
        mesocycle_id: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[Session], dict[str, int]]:
        """List sessions and return items with pagination metadata."""
        ...

    async def get(self, session_id: str) -> Session:
        """Get one session by ID."""
        ...

    async def delete(self, session_id: str) -> bool:
        """Delete one session."""
        ...

    async def add_exercise(self, session_id: str, payload: dict[str, object]) -> Session:
        """Add one exercise to a session."""
        ...

    async def update_exercise(
        self, session_exercise_id: str, payload: dict[str, object]
    ) -> SessionExercise:
        """Update one session exercise and return its latest state."""
        ...

    async def remove_exercise(self, session_exercise_id: str) -> bool:
        """Remove one exercise from a session."""
        ...

    async def add_set(
        self, session_exercise_id: str, payload: dict[str, object]
    ) -> SessionExercise:
        """Add one set to a session exercise and return latest set."""
        ...

    async def update_set(self, set_id: str, payload: dict[str, object]) -> SessionSet:
        """Update one session set."""
        ...

    async def remove_set(self, set_id: str) -> bool:
        """Remove one set from a session exercise."""
        ...

    async def log_set(
        self, set_id: str, payload: dict[str, int | float | str | None]
    ) -> SessionSet:
        """Log actual set performance."""
        ...
