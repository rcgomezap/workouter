"""Mesocycle repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.mesocycle import (
    Mesocycle,
    MesocyclePlannedSession,
    MesocycleWeek,
)


class MesocycleRepository(Protocol):
    """Persistence contract for mesocycles."""

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Mesocycle], dict[str, int]]:
        """List mesocycles and return items with pagination metadata."""
        ...

    async def get(self, mesocycle_id: str) -> Mesocycle:
        """Get one mesocycle by ID."""
        ...

    async def create(self, payload: dict[str, str]) -> Mesocycle:
        """Create one mesocycle."""
        ...

    async def update(self, mesocycle_id: str, payload: dict[str, str]) -> Mesocycle:
        """Update one mesocycle."""
        ...

    async def delete(self, mesocycle_id: str) -> bool:
        """Delete one mesocycle."""
        ...

    async def add_week(self, mesocycle_id: str, payload: dict[str, object]) -> MesocycleWeek:
        """Add one planning week to a mesocycle."""
        ...

    async def update_week(self, week_id: str, payload: dict[str, object]) -> MesocycleWeek:
        """Update one mesocycle planning week."""
        ...

    async def remove_week(self, week_id: str) -> bool:
        """Remove one mesocycle planning week."""
        ...

    async def add_session(
        self, mesocycle_week_id: str, payload: dict[str, object]
    ) -> MesocyclePlannedSession:
        """Add one planned session to a mesocycle week."""
        ...

    async def update_session(
        self, session_id: str, payload: dict[str, object]
    ) -> MesocyclePlannedSession:
        """Update one mesocycle planned session."""
        ...

    async def remove_session(self, session_id: str) -> bool:
        """Remove one mesocycle planned session."""
        ...
