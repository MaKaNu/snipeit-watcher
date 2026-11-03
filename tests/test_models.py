from snipeit_watcher.models import AssetManager, SnipeHistories


class TestAssetManager:
    def test_hash_method(self, user, assets):
        manager = AssetManager(asset_manager=user, assets=assets)

        result = hash(manager)
        assert isinstance(result, int)


class TestSnipeHistories:
    def test_by_action(self, history_create, history_checkout):
        histories = SnipeHistories(total=2, rows=[history_create, history_checkout])

        histories.by_action("checkout")

        assert histories.total == 1
        assert histories.rows[0] == history_checkout
