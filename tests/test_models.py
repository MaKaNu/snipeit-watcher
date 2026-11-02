from snipeit_watcher.models import AssetManager


class TestAssetManager:
    def test_hash_method(self, user, assets):
        manager = AssetManager(asset_manager=user, assets=assets)

        result = hash(manager)
        assert isinstance(result, int)
