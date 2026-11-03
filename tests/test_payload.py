import html5lib
import pytest
from html5lib.html5parser import ParseError

from snipeit_watcher.services.notifiers.payload import create_payload


def assert_valid_html(html_string, is_fragment=False):
    """
    Asserts that an HTML string is valid and well-formed.
    Set is_fragment=True if your template only outputs a partial snippet (e.g. <div>...</div>)
    rather than a full <!DOCTYPE> document.
    """
    parser = html5lib.HTMLParser(strict=True)
    try:
        if is_fragment:
            parser.parseFragment(html_string)
        else:
            parser.parse(html_string)
    except ParseError as e:
        pytest.fail(f"Invalid HTML output:\n{e}\n\nRendered HTML was:\n{html_string}")


class TestOverloadedCreatePayload:
    def test_create_payload_asset_manager(self, asset_manager):
        payload = create_payload(asset_manager)
        assert payload
        assert isinstance(payload.title, str)
        assert payload.body_format == "html"
        assert_valid_html(payload.message)

    def test_create_payload_asset_manager_missing_assigned(self, asset_manager, assets):
        asset_manager.assets = assets
        with pytest.raises(RuntimeError):
            create_payload(asset_manager)
