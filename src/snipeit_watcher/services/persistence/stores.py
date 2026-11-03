from collections.abc import Iterator, MutableMapping
from typing import Any

from persidict import FileDirDict, S3Dict

from snipeit_watcher.config import settings
from snipeit_watcher.models import AssetManager
from snipeit_watcher.types import StoreType


class PersistentStore(MutableMapping):
    def __init__(self):
        self._store: StoreType = settings.store
        self._store_path = settings.store_path
        self._backend = self._initalize_backend()

    def _initalize_backend(self) -> MutableMapping:
        match self._store:
            case StoreType.FILE:
                return FileDirDict(base_dir=str(self._store_path), serialization_format="json")
            case StoreType.S3:
                return S3Dict(bucket_name=str(self._store_path), serialization_format="json")
            case _:
                raise NotImplementedError(f"Unkown storage type: {self._store}")

    def __getitem__(self, key: str) -> Any:
        return self._backend[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._backend[key] = value

    def __delitem__(self, key: str) -> None:
        del self._backend[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._backend)

    def __len__(self) -> int:
        return len(self._backend)


persitent_store = PersistentStore()


def store_asset_manager(asset_manager: AssetManager) -> None:
    persitent_store["asset_managers"] = {asset_manager.asset_manager.id: hash(asset_manager)}


def is_asset_manager_updated(asset_manager: AssetManager) -> bool:
    return hash(asset_manager) != persitent_store.get("asset_managers", {}).get(
        str(asset_manager.asset_manager.id), hash(0)
    )
