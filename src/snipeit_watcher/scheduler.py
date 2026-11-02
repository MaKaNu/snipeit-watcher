import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from snipeit_watcher.config import settings
from snipeit_watcher.models import AssetManager
from snipeit_watcher.services.notifiers.manager import build_notification_manager
from snipeit_watcher.services.notifiers.payload import create_payload
from snipeit_watcher.services.snipeit_api_client import SnipeitAPIClient

logger = logging.getLogger(__name__)
client = SnipeitAPIClient()
scheduler = AsyncIOScheduler()
notification_manager = build_notification_manager()


async def scheduled_watcher():
    users = await client.get_disabled_users()
    logger.info(f"Following Users: {[(user.id, user.name) for user in users.rows]}")


async def scheduled_analyze_disabled_users():
    """Checks if disabled users have assets and reacts."""
    users = await client.get_disabled_users()
    managers_by_id: dict[int, AssetManager] = {}
    for user in users.rows:
        if user.assets_count > 0:
            await client.get_asset_managers(user, managers_by_id)
        else:
            pass  # delete_user
            continue

    for manager in managers_by_id.values():
        payload = create_payload(manager)
        await notification_manager.notify_all(payload)


def init_scheduler():
    scheduler.add_job(
        scheduled_analyze_disabled_users,
        "interval",
        seconds=settings.watcher_interval,
        id="watcher_analyze_disabled_users",
        replace_existing=True,
    )
    scheduler.start()
