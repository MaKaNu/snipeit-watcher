import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from snipeit_watcher import scheduler as scheduler_module
from snipeit_watcher.models import SnipeUser, SnipeUsers


def test_init_scheduler_registers_and_starts_job(monkeypatch):
    scheduler = MagicMock()
    monkeypatch.setattr(scheduler_module, "scheduler", scheduler)

    scheduler_module.init_scheduler()

    scheduler.add_job.assert_called_once_with(
        scheduler_module.scheduled_watcher,
        "interval",
        seconds=scheduler_module.settings.watcher_interval,
        id="watcher_",
        replace_existing=True,
    )
    scheduler.start.assert_called_once_with()


@pytest.mark.asyncio
async def test_scheduled_watcher_fetches_and_logs_users(monkeypatch, caplog):
    caplog.set_level(logging.INFO, logger=scheduler_module.logger.name)

    users = SnipeUsers(
        total=1,
        rows=[SnipeUser(id=1, name="Example", username="example")],
        current_page=1,
        per_page=1,
        total_pages=1,
    )
    get_disabled_users = AsyncMock(return_value=users)
    monkeypatch.setattr(scheduler_module.client, "get_disabled_users", get_disabled_users)

    await scheduler_module.scheduled_watcher()

    get_disabled_users.assert_awaited_once_with()
    assert "Following Users: [(1, 'Example')]" in caplog.text


@pytest.mark.asyncio
async def test_init_scheduler_registers_job_and_starts():
    try:
        scheduler_module.init_scheduler()
        job = scheduler_module.scheduler.get_job("watcher_")
        assert job
        assert scheduler_module.scheduler.running
        assert job.func is scheduler_module.scheduled_watcher
        assert job.trigger.interval.total_seconds() == scheduler_module.settings.watcher_interval
    finally:
        scheduler_module.scheduler.shutdown(wait=False)


@pytest.mark.asyncio
async def test_job_fires(monkeypatch):
    monkeypatch.setattr(scheduler_module.settings, "watcher_interval", 0.05)
    fired = asyncio.Event()

    async def fake():
        fired.set()

    monkeypatch.setattr(
        scheduler_module, "scheduled_watcher", fake
    )  # patched before init_scheduler
    monkeypatch.setattr(scheduler_module, "scheduler", AsyncIOScheduler())
    scheduler_module.init_scheduler()
    try:
        await asyncio.wait_for(fired.wait(), timeout=1)
    finally:
        scheduler_module.scheduler.shutdown(wait=False)
