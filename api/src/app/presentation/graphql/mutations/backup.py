from datetime import datetime

import strawberry
from strawberry.types import Info

from app.presentation.graphql.context import Context


@strawberry.type
class BackupResult:
    success: bool
    filename: str | None
    size_bytes: int | None
    created_at: datetime

@strawberry.type
class BackupMutation:
    @strawberry.mutation
    async def trigger_backup(self, info: Info[Context, None]) -> BackupResult:
        res = await info.context.backup_service.trigger_backup()
        return BackupResult(
            success=res.success,
            filename=res.filename,
            size_bytes=res.size_bytes,
            created_at=res.created_at
        )
