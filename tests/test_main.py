from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from snipeit_watcher.api.routes import client as route_client
from snipeit_watcher.main import app, scheduler
from snipeit_watcher.models import SnipeUser, SnipeUsers

client = TestClient(app)


@pytest.fixture
def users():
    users = SnipeUsers(
        total=1,
        rows=[
            SnipeUser(
                id=42,
                name="Disabled User",
                username="disabled.user",
                email="disabled@example.com",
            )
        ],
        current_page=1,
        per_page=50,
        total_pages=1,
    )
    return users


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_users_disabled(monkeypatch, users):

    get_disabled_users = AsyncMock(return_value=users)
    monkeypatch.setattr(route_client, "get_disabled_users", get_disabled_users)

    response = client.post("/users_disabled")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Execution triggered successfully",
        "result": {
            "total": 1,
            "rows": [
                {
                    "id": 42,
                    "name": "Disabled User",
                    "username": "disabled.user",
                    "email": "disabled@example.com",
                    "assets_count": 0,
                }
            ],
            "current_page": 1,
            "per_page": 50,
            "total_pages": 1,
            "prev_page_url": None,
            "next_page_url": None,
        },
    }
    get_disabled_users.assert_awaited_once_with()


def test_lifespan_starts_and_stops_scheduler():
    with TestClient(app):
        assert scheduler.running
    assert not scheduler.running
