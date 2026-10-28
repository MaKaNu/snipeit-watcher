from abc import ABC, abstractmethod

import apprise

from snipeit_watcher.models import NotificationPayload


class BaseNotifier(ABC):
    @abstractmethod
    async def send(self, payload: NotificationPayload) -> apprise.AppriseResult: ...
