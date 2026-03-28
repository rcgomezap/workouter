"""Backup application service."""

from __future__ import annotations

from workouter_cli.domain.entities.backup import BackupResult
from workouter_cli.domain.repositories.backup import BackupRepository


class BackupService:
    """Backup use-cases orchestration."""

    def __init__(self, backup_repository: BackupRepository) -> None:
        self.backup_repository = backup_repository

    async def trigger(self) -> BackupResult:
        return await self.backup_repository.trigger()
