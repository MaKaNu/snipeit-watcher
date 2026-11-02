from jinja2 import Environment, PackageLoader, select_autoescape
from multipledispatch import dispatch

from snipeit_watcher.config import settings
from snipeit_watcher.models import AssetManager, NotificationPayload, SnipeAsset, SnipeUser

_env = Environment(
    loader=PackageLoader("snipeit_watcher", "templates"),
    autoescape=select_autoescape(["html", "xml", "j2"], default_for_string=True),
)


@dispatch(AssetManager)
def create_payload(data: AssetManager):
    for asset in data.assets:
        if not asset.assigned_to:
            raise RuntimeError("Asset is not assigned to anybody.")  # noqa: TRY003

    message = _env.get_template("payload_asset_manager.html.j2").render(
        manager=data,
        assets=data.assets,
        snipeit_url=str(settings.app_url),
    )
    return NotificationPayload(
        title="[SNIPEIT WATCHER] New Disabled User(s)",
        message=message,
        recipient=data.asset_manager.email,
        body_format="html",
    )


if __name__ == "__main__":
    manager_user = SnipeUser(id=1, name="Piet", username="pietbro", email="pietbro@example.com")
    user_1 = SnipeUser(id=2, name="Carol", username="carolbot", email="carolbot@example.com")
    user_2 = SnipeUser(id=3, name="Tobi", username="tobitobsen", email="tobitobsen@example.com")
    assets = [
        SnipeAsset(id=1, name="NewAsset", asset_tag="asset_001", assigned_to=user_1),
        SnipeAsset(id=2, name="NewAsset 2", asset_tag="asset_002", assigned_to=user_2),
    ]
    manager = AssetManager(asset_manager=manager_user, assets=assets)

    payload = create_payload(manager)

    print(payload.title)
    print(payload.message)
    print(payload.recipient)
