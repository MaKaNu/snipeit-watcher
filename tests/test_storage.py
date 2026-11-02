from pathlib import Path

from snipeit_watcher.models import AssetManager, SnipeAsset
from snipeit_watcher.services.persistence.stores import (
    PersistentStore,
    is_asset_manager_updated,
    store_asset_manager,
)
from snipeit_watcher.types import StoreType


def test_file_storage(tmp_path, monkeypatch):
    from snipeit_watcher.config import settings

    monkeypatch.setattr(settings, "store", StoreType.FILE)
    monkeypatch.setattr(settings, "store_path", tmp_path)

    storage = PersistentStore()
    storage["k"] = {"a": 1}

    assert storage["k"] == {"a": 1}
    assert Path(storage._store_path).exists()
    del storage["k"]
    assert "k" not in storage


def test_store_asset_manager(tmp_path, monkeypatch, user, assets):
    from snipeit_watcher.config import settings
    from snipeit_watcher.services.persistence import stores

    monkeypatch.setattr(settings, "store", StoreType.FILE)
    monkeypatch.setattr(settings, "store_path", tmp_path)
    monkeypatch.setattr(stores, "persitent_store", stores.PersistentStore())

    manager = AssetManager(asset_manager=user, assets=assets)

    store_asset_manager(manager)
    assert not is_asset_manager_updated(manager)
    manager.assets[1] = SnipeAsset(id=3, name="TestAsset003", asset_tag="testasset003")
    assert is_asset_manager_updated(manager)
