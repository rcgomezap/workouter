from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.infrastructure.backup.manager import BackupManager
import structlog

logger = structlog.get_logger(__name__)

class BackupScheduler:
    def __init__(self, manager: BackupManager) -> None:
        self.manager = manager
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        if not self.manager.config.backup.scheduled.enabled:
            logger.info("scheduled_backups_disabled")
            return

        frequency_hours = self.manager.config.backup.scheduled.frequency_hours
        
        self.scheduler.add_job(
            self.manager.trigger_backup,
            trigger=IntervalTrigger(hours=frequency_hours),
            id="backup_job",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("scheduled_backups_started", frequency_hours=frequency_hours)

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("scheduled_backups_shutdown")
