import os
import pathlib
import shutil
from datetime import UTC, datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncEngine

from app.application.services.backup_service import BackupResult, BackupService
from app.config.schema import Config

logger = structlog.get_logger(__name__)

class BackupManager(BackupService):
    def __init__(self, config: Config, engine: AsyncEngine) -> None:
        self.config = config
        self.engine = engine
        self.backup_dir = pathlib.Path(self.config.backup.directory)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def trigger_backup(self) -> BackupResult:
        if not self.config.backup.enabled:
            return BackupResult(success=False, error="Backup system is disabled")

        if not self.config.database.url.startswith("sqlite"):
            return BackupResult(success=False, error="Backup currently only supports SQLite")

        try:
            # Extract database path from SQLAlchemy URL
            # Example: sqlite+aiosqlite:///./data/workout_tracker.db
            db_path_str = self.config.database.url.split("///")[-1]
            db_path = pathlib.Path(db_path_str)

            if not db_path.exists():
                return BackupResult(success=False, error=f"Database file not found: {db_path}")

            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename

            # For SQLite, we should ideally use a checkpoint, but shutil.copy2 is simple
            # and works if there are no active writes.
            # In a production-grade app, we'd use 'VACUUM INTO' or similar.
            shutil.copy2(db_path, backup_path)
            
            size_bytes = backup_path.stat().st_size
            created_at = datetime.now(UTC)

            logger.info("backup_created", filename=backup_filename, size_bytes=size_bytes)

            self._rotate_backups()

            return BackupResult(
                success=True,
                filename=backup_filename,
                size_bytes=size_bytes,
                created_at=created_at
            )
        except Exception as e:
            logger.exception("backup_failed", error=str(e))
            return BackupResult(success=False, error=str(e))

    def _rotate_backups(self) -> None:
        backups = sorted(
            [f for f in self.backup_dir.glob("backup_*.db")],
            key=os.path.getmtime
        )

        if len(backups) > self.config.backup.max_backups:
            to_delete = backups[:-self.config.backup.max_backups]
            for f in to_delete:
                f.unlink()
                logger.info("backup_rotated", filename=f.name)
