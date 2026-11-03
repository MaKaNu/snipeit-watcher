import asyncio

import pytest

import snipeit_watcher.scheduler as scheduler_module


@pytest.mark.asyncio
async def test_init_scheduler_registers_and_starts_job():
    scheduler = scheduler_module.init_scheduler()
    try:
        job = scheduler.get_job("watcher_analyze_disabled_users")
        assert job
        assert scheduler.running
        assert job.func is scheduler_module.scheduled_analyze_disabled_users
        assert job.trigger.interval.total_seconds() == scheduler_module.settings.watcher_interval
    finally:
        scheduler.shutdown(wait=False)


@pytest.mark.asyncio
async def test_job_fires(monkeypatch):
    monkeypatch.setattr(scheduler_module.settings, "watcher_interval", 0.05)
    fired = asyncio.Event()

    async def fake():
        fired.set()

    monkeypatch.setattr(scheduler_module, "scheduled_analyze_disabled_users", fake)
    scheduler = scheduler_module.init_scheduler()
    try:
        await asyncio.wait_for(fired.wait(), timeout=1)
    finally:
        scheduler.shutdown(wait=False)
