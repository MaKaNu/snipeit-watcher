import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from snipeit_watcher.config import settings
from snipeit_watcher.scheduler.analyze_disabled_user import scheduled_analyze_disabled_users

logger = logging.getLogger(__name__)


def init_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    logger.info("Creating Scheduled Job analyze disabled users")
    scheduler.add_job(
        scheduled_analyze_disabled_users,
        "interval",
        seconds=settings.watcher_interval,
        id="watcher_analyze_disabled_users",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler
