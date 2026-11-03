from jinja2 import Environment, PackageLoader, select_autoescape
from multipledispatch import dispatch

from snipeit_watcher.config import settings
from snipeit_watcher.models import AssetManager, NotificationPayload

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
