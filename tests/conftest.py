import os

import pytest

from snipeit_watcher.models import SnipeAsset, SnipeUser

# Must be set before snipeit_watcher.config is imported (it instantiates Settings at import time).
os.environ.setdefault("SNIPEIT_API_TOKEN", "test-token")


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
