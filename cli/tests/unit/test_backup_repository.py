from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.infrastructure.graphql.mutations.backup import TRIGGER_BACKUP
from workouter_cli.infrastructure.repositories.backup import GraphQLBackupRepository


@pytest.mark.asyncio
async def test_repository_trigger_maps_backup_result() -> None:
    client = AsyncMock()
    client.execute = AsyncMock(
        return_value={
            "triggerBackup": {
                "success": True,
                "filename": "backup-20260101.sql",
                "sizeBytes": 1024,
                "createdAt": "2026-01-01T10:00:00Z",
            }
        }
    )

    repository = GraphQLBackupRepository(client=client)
    result = await repository.trigger()

    assert result.success is True
    assert result.filename == "backup-20260101.sql"
    client.execute.assert_awaited_once_with(TRIGGER_BACKUP, {})
