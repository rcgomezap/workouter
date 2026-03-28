from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.application.services.backup_service import BackupService
from workouter_cli.domain.entities.backup import BackupResult


def _backup_result() -> BackupResult:
    return BackupResult(
        success=True,
        filename="backup-20260101.sql",
        size_bytes=1024,
        created_at="2026-01-01T10:00:00Z",
    )


@pytest.mark.asyncio
async def test_backup_service_trigger_delegates(mocker) -> None:  # type: ignore[no-untyped-def]
    repository = mocker.Mock()
    repository.trigger = AsyncMock(return_value=_backup_result())
    service = BackupService(backup_repository=repository)

    result = await service.trigger()

    assert result.success is True
    repository.trigger.assert_awaited_once_with()
