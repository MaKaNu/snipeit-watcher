from snipeit_watcher.config import settings
from snipeit_watcher.models import NotificationPayload
from snipeit_watcher.services.notifiers.base import BaseNotifier
from snipeit_watcher.services.notifiers.providers import MailNotifier


class NotificationManager:
    def __init__(self) -> None:
        self._notifiers: list[BaseNotifier] = []

    def register(self, notifier: BaseNotifier):
        self._notifiers.append(notifier)
        return self

    async def notify_all(self, payload: NotificationPayload) -> None:
        for notifier in self._notifiers:
            await notifier.send(payload)


def build_notification_manager() -> NotificationManager:
    manager = NotificationManager()

    if settings.mail_host:
        manager.register(MailNotifier(config=settings))

    return manager
