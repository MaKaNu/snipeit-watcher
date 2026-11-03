import os

import pytest

from snipeit_watcher.models import AssetManager, SnipeAsset, SnipeHistory, SnipeItem, SnipeUser

# Must be set before snipeit_watcher.config is imported (it instantiates Settings at import time).
os.environ.setdefault("SNIPEIT_API_TOKEN", "test-token")


# Global Fixtures
@pytest.fixture
def user():
    return SnipeUser(
        id=1,
        name="Tester",
        username="tester",
    )


@pytest.fixture
def assets():
    return [
        SnipeAsset(id=1, name="TestAsset001", asset_tag="testasset001"),
        SnipeAsset(id=2, name="TestAsset002", asset_tag="testasset002"),
    ]


@pytest.fixture
def assigned_assets(user):
    return [
        SnipeAsset(id=1, name="TestAsset001", asset_tag="testasset001", assigned_to=user),
        SnipeAsset(id=2, name="TestAsset002", asset_tag="testasset002", assigned_to=user),
    ]


@pytest.fixture
def item():
    return SnipeItem(id=1, name="Test Item", type="asset")


@pytest.fixture
def history_create(user, item):
    return SnipeHistory(id=1, created_by=user, action_type="create new", item=item)


@pytest.fixture
def history_checkout(user, item):
    return SnipeHistory(id=2, created_by=user, action_type="checkout", item=item)


@pytest.fixture
def asset_manager(user, assigned_assets):
    return AssetManager(asset_manager=user, assets=assigned_assets)
