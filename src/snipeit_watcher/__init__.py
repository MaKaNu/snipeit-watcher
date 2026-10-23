import asyncio

from snipeit_watcher.models import NotificationPayload
from snipeit_watcher.notifiers.manager import build_notification_manager


async def async_main():
    print("Starting main loop...")
    await notification()
    while True:
        await asyncio.sleep(30)


async def notification():
    notifier = build_notification_manager()

    # Dispatching a validated payload:
    payload = NotificationPayload(
        title="SCIM Deactivation Alert",
        message="User John Doe was deactivated via SCIM but still holds 2 assets.",
    )

    await notifier.notify_all(payload)


def main():
    """Synchronous entry point wrapper"""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("Shutting down gracefully.")
