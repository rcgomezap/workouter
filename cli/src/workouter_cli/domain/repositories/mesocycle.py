"""Mesocycle repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.mesocycle import Mesocycle


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
