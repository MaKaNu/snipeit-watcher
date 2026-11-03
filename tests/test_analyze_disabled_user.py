from types import SimpleNamespace

import pytest

from snipeit_watcher.models import AssetManager, SnipeAsset, SnipeUser, SnipeUsers
from snipeit_watcher.scheduler import analyze_disabled_user as module


def make_user(user_id: int, assets_count: int) -> SnipeUser:
    return SnipeUser(id=user_id, name=f"user{user_id}", assets_count=assets_count)


def make_manager(manager_id: int) -> AssetManager:
    manager = SnipeUser(id=manager_id, name=f"manager{manager_id}")
    asset = SnipeAsset(id=manager_id, name=f"asset{manager_id}", asset_tag=f"T{manager_id}")
    return AssetManager(asset_manager=manager, assets=[asset])


class FakeClient:
    """Returns the given users; maps each user id to the manager that gets resolved."""

    def __init__(self, users: list[SnipeUser], managers: dict[int, AssetManager] | None = None):
        self.users = users
        self.managers = managers or {}
        self.deleted: list[int] = []

    async def get_disabled_users(self) -> SnipeUsers:
        return SnipeUsers(total=len(self.users), rows=self.users)

    async def get_asset_managers(self, user, managers_by_id):
        manager = self.managers[user.id]
        managers_by_id[manager.asset_manager.id] = manager

    async def del_user(self, user):
        self.deleted.append(user.id)


class FakeNotifier:
    def __init__(self):
        self.sent = []

    async def notify_all(self, payload):
        self.sent.append(payload)


@pytest.fixture
def env(monkeypatch):
    """Patches persistence and notifier; exposes what was stored/sent."""

    e = SimpleNamespace(stored=[], notifier=FakeNotifier(), updated=True)
    monkeypatch.setattr(module, "is_asset_manager_updated", lambda m: e.updated)
    monkeypatch.setattr(module, "store_asset_manager", e.stored.append)
    monkeypatch.setattr(module, "create_payload", lambda m: m)
    monkeypatch.setattr(module, "notification_manager", e.notifier)

    def use_client(client):
        monkeypatch.setattr(module, "client", client)
        return client

    e.use_client = use_client
    return e


@pytest.mark.asyncio
async def test_user_without_assets_is_deleted_and_not_notified(env):
    client = env.use_client(FakeClient([make_user(1, assets_count=0)]))

    await module.scheduled_analyze_disabled_users()

    assert client.deleted == [1]
    assert env.notifier.sent == []
    assert env.stored == []


@pytest.mark.asyncio
async def test_user_with_assets_notifies_manager_and_is_not_deleted(env):
    manager = make_manager(10)
    client = env.use_client(FakeClient([make_user(1, assets_count=2)], {1: manager}))

    await module.scheduled_analyze_disabled_users()

    assert client.deleted == []
    assert env.stored == [manager]
    assert env.notifier.sent == [manager]


@pytest.mark.asyncio
async def test_shared_manager_is_notified_once(env):
    manager = make_manager(10)
    env.use_client(FakeClient([make_user(1, 1), make_user(2, 1)], {1: manager, 2: manager}))

    await module.scheduled_analyze_disabled_users()

    assert env.notifier.sent == [manager]


@pytest.mark.asyncio
async def test_unchanged_manager_is_skipped(env):
    env.updated = False
    env.use_client(FakeClient([make_user(1, 1)], {1: make_manager(10)}))

    await module.scheduled_analyze_disabled_users()

    assert env.stored == []
    assert env.notifier.sent == []


@pytest.mark.asyncio
async def test_mixed_users(env):
    manager = make_manager(10)
    client = env.use_client(FakeClient([make_user(1, 0), make_user(2, 3)], {2: manager}))

    await module.scheduled_analyze_disabled_users()

    assert client.deleted == [1]
    assert env.notifier.sent == [manager]
