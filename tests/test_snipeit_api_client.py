import pytest
import respx

from snipeit_watcher.services.snipeit_api_client import SnipeitAPIClient


@pytest.fixture
def api_client():
    """Fixture to provide a clean instance of the client for each test."""
    client = SnipeitAPIClient()
    return client


@pytest.mark.asyncio
@respx.mock
async def test_get_disabled_users_without_whitelist(api_client):
    """Test GET method with querry to get disabled users."""
    respx.get(
        f"{api_client.base_url}api/v1/users?sort=created_at&order=desc&activated=false&all=false"
    ).respond(
        status_code=200,
        json={
            "total": 0,
            "rows": [],
            "current_page": 1,
            "per_page": 0,
            "total_pages": 0,
        },
    )

    result = await api_client.get_disabled_users()

    assert result == "TODO"
