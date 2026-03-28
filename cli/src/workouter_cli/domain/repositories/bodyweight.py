"""Bodyweight repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.bodyweight import BodyweightLog


class BodyweightRepository(Protocol):
    """Persistence contract for bodyweight logs."""

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[BodyweightLog], dict[str, int]]:
        """List bodyweight logs and return items with pagination metadata."""
        ...

    async def log(self, payload: dict[str, str | float | None]) -> BodyweightLog:
        """Create one bodyweight log entry."""
        ...

    async def update(
        self,
        bodyweight_log_id: str,
        payload: dict[str, str | float | None],
    ) -> BodyweightLog:
        """Update one bodyweight log entry."""
        ...

    async def delete(self, bodyweight_log_id: str) -> bool:
        """Delete one bodyweight log entry."""
        ...
