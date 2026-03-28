"""GraphQL-backed backup repository implementation."""

from __future__ import annotations

from workouter_cli.domain.entities.backup import BackupResult
from workouter_cli.domain.repositories.backup import BackupRepository
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.graphql.mappers.response_mapper import map_backup_result
from workouter_cli.infrastructure.graphql.mutations.backup import TRIGGER_BACKUP


class GraphQLBackupRepository(BackupRepository):
    """Backup repository using GraphQL API operations."""

    def __init__(self, client: GraphQLClient) -> None:
        self.client = client

    async def trigger(self) -> BackupResult:
        result = await self.client.execute(TRIGGER_BACKUP, {})
        return map_backup_result(result["triggerBackup"])
