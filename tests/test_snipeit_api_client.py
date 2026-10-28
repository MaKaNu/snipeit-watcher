import pytest
import respx

from snipeit_watcher.config import settings
from snipeit_watcher.models import SnipeUsers
from snipeit_watcher.services.snipeit_api_client import SnipeitAPIClient


@pytest.fixture
def api_client():
    """Fixture to provide a clean instance of the client for each test."""
    client = SnipeitAPIClient()
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("whitelist", "expected_ids"),
    [
        (set(), [1, 2]),
        ({2}, [1]),
    ],
    ids=("NoWhitelist", "WithWhitelist"),
)
@respx.mock
async def test_get_disabled_users(api_client, monkeypatch, whitelist, expected_ids):
    """Test GET method with querry to get disabled users."""
    monkeypatch.setattr(settings, "disabled_users_id_whitelist", whitelist)

    respx.get(
        f"{api_client.base_url}api/v1/users",
        params={
            "sort": "created_at",
            "order": "desc",
            "activated": "false",
            "all": "false",
        },
    ).respond(
        status_code=200,
        json={
            "total": 2,
            "rows": [
                {"id": 1, "name": "User One", "username": "user1"},
                {"id": 2, "name": "User Two", "username": "user2"},
            ],
            "current_page": 1,
            "per_page": 2,
            "total_pages": 1,
        },
    )

    result = await api_client.get_disabled_users()

    assert isinstance(result, SnipeUsers)
    assert [user.id for user in result.rows] == expected_ids
    assert result.total == len(expected_ids)


@pytest.mark.asyncio
async def test_close_client(api_client):
    assert api_client._client.is_closed is False
    await api_client.close()
    assert api_client._client.is_closed
