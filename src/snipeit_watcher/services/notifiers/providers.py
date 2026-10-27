from urllib.parse import quote

import apprise

from snipeit_watcher.config import Settings
from snipeit_watcher.models import NotificationPayload
from snipeit_watcher.services.notifiers.base import BaseNotifier


class MailNotifier(BaseNotifier):
    def __init__(self, config: Settings) -> None:
        self.url = (
            f"mailto://{config.mail_host}:{config.mail_port}"
            f"?from={quote(str(config.mail_from_addr))}"
            f"&name={quote(str(config.mail_from_name))}"
        )

    async def send(self, payload: NotificationPayload) -> apprise.AppriseResult:
        # Fresh instance per send: add() accumulates servers, so a shared
        # instance would re-notify all previous recipients.
        ap = apprise.Apprise()
        if not ap.add(self.url + f"&to={quote(str(payload.recipient))}"):
            raise RuntimeError(f"Invalid notification URL for {payload.recipient}")  # noqa: TRY003
        return ap.notify(body=payload.message, title=payload.title)
