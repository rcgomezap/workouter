"""Backup repository protocol."""

from __future__ import annotations

from typing import Protocol

from workouter_cli.domain.entities.backup import BackupResult


class BackupRepository(Protocol):
    """Persistence contract for backup operations."""

    async def trigger(self) -> BackupResult:
        """Trigger one backup operation."""
        ...
