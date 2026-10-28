import asyncio
import socket
from unittest.mock import MagicMock

import apprise
import pytest
from aiosmtpd.controller import Controller

from snipeit_watcher.config import Settings
from snipeit_watcher.models import NotificationPayload
from snipeit_watcher.services.notifiers import manager as manager_module
from snipeit_watcher.services.notifiers import providers
from snipeit_watcher.services.notifiers.base import BaseNotifier
from snipeit_watcher.services.notifiers.manager import NotificationManager

PAYLOAD = NotificationPayload(title="t", message="m", recipient="test@example.com")


class FakeNotifier(BaseNotifier):
    def __init__(self) -> None:
        self.sent: list[NotificationPayload] = []

    async def send(self, payload: NotificationPayload) -> apprise.AppriseResult:
        self.sent.append(payload)
        return apprise.AppriseResult()


def test_manager_dispatches_to_all():
    a, b = FakeNotifier(), FakeNotifier()
    mgr = NotificationManager().register(a).register(b)
    asyncio.run(mgr.notify_all(PAYLOAD))
    assert a.sent == [PAYLOAD] and b.sent == [PAYLOAD]


def test_mail_notifier_uses_mocked_apprise(monkeypatch):
    fake_ap = MagicMock()
    monkeypatch.setattr(providers.apprise, "Apprise", lambda: fake_ap)
    cfg = Settings(
        _env_file=None,  # pyright: ignore[reportCallIssue]
        snipeit_api_token="x",  # noqa: S106
        mail_host="localhost",
        mail_from_addr="from@example.com",
    )
    notifier = providers.MailNotifier(config=cfg)
    asyncio.run(notifier.send(PAYLOAD))
    assert "mailto://localhost:25" in fake_ap.add.call_args.args[0]
    fake_ap.notify.assert_called_once_with(body="m", title="t")


def test_build_manager_registers_mail_only_when_configured(monkeypatch):
    monkeypatch.setattr(providers.apprise, "Apprise", MagicMock)
    unconfigured = Settings(
        _env_file=None,  # pyright: ignore[reportCallIssue]
        snipeit_api_token="x",  # noqa: S106 pyright
    )
    monkeypatch.setattr(manager_module, "settings", unconfigured)
    assert manager_module.build_notification_manager()._notifiers == []

    configured = Settings(
        _env_file=None,  # pyright: ignore[reportCallIssue]
        snipeit_api_token="x",  # noqa: S106
        mail_host="localhost",
    )
    monkeypatch.setattr(manager_module, "settings", configured)
    assert len(manager_module.build_notification_manager()._notifiers) == 1


class _Collector:
    def __init__(self) -> None:
        self.envelopes: list = []

    async def handle_DATA(self, server, session, envelope):
        self.envelopes.append(envelope)
        return "250 OK"


@pytest.fixture
def smtp_server():
    handler = _Collector()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    controller = Controller(handler, hostname="127.0.0.1", port=port)
    controller.start()
    try:
        yield handler, port
    finally:
        controller.stop()


@pytest.fixture
def smtp_cfg(smtp_server):
    _, port = smtp_server
    return Settings(
        _env_file=None,  # pyright: ignore[reportCallIssue]
        snipeit_api_token="x",  # noqa: S106
        mail_host="127.0.0.1",
        mail_port=port,
        mail_from_addr="from@example.com",
    )


@pytest.fixture
def dummy_payload():
    return NotificationPayload(title="Hello", message="Body", recipient="to@example.com")


def test_mail_notifier_delivers_to_smtp_server(smtp_server, smtp_cfg, dummy_payload):
    handler, _ = smtp_server
    notifier = providers.MailNotifier(config=smtp_cfg)
    asyncio.run(notifier.send(dummy_payload))
    asyncio.run(notifier.send(dummy_payload.model_copy(update={"recipient": "two@example.com"})))

    assert [e.rcpt_tos for e in handler.envelopes] == [["to@example.com"], ["two@example.com"]]
    assert handler.envelopes[0].mail_from == "from@example.com"
    assert b"Subject: Hello" in handler.envelopes[0].content
