from pathlib import Path

import boto3
import pytest
from moto import mock_aws

from snipeit_watcher.models import AssetManager, SnipeAsset
from snipeit_watcher.services.persistence.stores import (
    PersistentStore,
    is_asset_manager_updated,
    store_asset_manager,
)
from snipeit_watcher.types import StoreType


@pytest.fixture
def store_config(request, tmp_path, monkeypatch):
    """Yield (store type, store path); S3 runs against a moto-mocked bucket."""
    from snipeit_watcher.config import settings

    store_type = request.param
    if store_type == StoreType.S3:
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
        monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
        with mock_aws():
            boto3.client("s3").create_bucket(Bucket="test-bucket")
            monkeypatch.setattr(settings, "store", store_type)
            monkeypatch.setattr(settings, "store_path", "test-bucket")
            yield store_type, "test-bucket"
    else:
        monkeypatch.setattr(settings, "store", store_type)
        monkeypatch.setattr(settings, "store_path", tmp_path)
        yield store_type, tmp_path


@pytest.mark.parametrize("store_config", [StoreType.FILE, StoreType.S3], indirect=True)
class TestStorage:
    def test_storage(self, store_config):
        storage = PersistentStore()
        storage["k"] = {"a": 1}

        assert storage["k"] == {"a": 1}
        if store_config[0] == StoreType.FILE:
            assert Path(storage._store_path).exists()
        del storage["k"]
        assert "k" not in storage

    def test_storage_len(self, store_config):
        storage = PersistentStore()
        assert len(storage) == 0
        storage["k"] = 5
        assert len(storage) == 1

    def test_storage_iter(self, store_config):
        storage = PersistentStore()

        storage["k"] = 1
        storage["l"] = 2
        result = 0
        for key in storage:
            result += storage[key]
        assert result == 3

    def test_store_asset_manager(self, store_config, monkeypatch, user, assets):
        from snipeit_watcher.services.persistence import stores

        monkeypatch.setattr(stores, "persitent_store", stores.PersistentStore())

        manager = AssetManager(asset_manager=user, assets=assets)

        store_asset_manager(manager)
        assert not is_asset_manager_updated(manager)
        manager.assets[1] = SnipeAsset(id=3, name="TestAsset003", asset_tag="testasset003")
        assert is_asset_manager_updated(manager)


def test_store_wrong_configured(monkeypatch):
    from snipeit_watcher.config import settings

    monkeypatch.setattr(settings, "store", "notimplemented")
    with pytest.raises(NotImplementedError) as e:
        PersistentStore()

    assert "notimplemented" in str(e.value)
