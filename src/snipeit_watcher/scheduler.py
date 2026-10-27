import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from snipeit_watcher.config import settings
from snipeit_watcher.services.snipeit_api_client import SnipeitAPIClient

logger = logging.getLogger(__name__)
client = SnipeitAPIClient()
scheduler = AsyncIOScheduler()


async def scheduled_watcher():
    users = await client.get_disabled_users()
    logger.info(f"Following Users: {[(user.id, user.name) for user in users.rows]}")


def init_scheduler():
    scheduler.add_job(
        scheduled_watcher,
        "interval",
        seconds=settings.watcher_interval,
        id="watcher_",
        replace_existing=True,
    )
    scheduler.start()
