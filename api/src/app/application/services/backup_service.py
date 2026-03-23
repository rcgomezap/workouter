from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

@dataclass
class BackupResult:
    success: bool
    filename: str | None = None
    size_bytes: int | None = None
    created_at: datetime | None = None
    error: str | None = None

class BackupService(Protocol):
    async def trigger_backup(self) -> BackupResult:
        ...
