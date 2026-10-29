from unittest.mock import AsyncMock

import httpx
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


def test_health_when_snipeit_is_reachable(monkeypatch):
    request = AsyncMock(return_value={"version": "1.0"})
    monkeypatch.setattr(route_client, "_request", request)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": {
            "snipeit_con": "healthy",
            "watcher_con": "healthy",
        }
    }
    request.assert_awaited_once_with("GET", "/version")


def test_health_when_snipeit_is_unreachable(monkeypatch):
    request = AsyncMock(side_effect=httpx.ConnectError("Snipe-IT unavailable"))
    monkeypatch.setattr(route_client, "_request", request)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": {
            "snipeit_con": "unhealthy Snipe-IT unavailable",
            "watcher_con": "healthy",
        }
    }
    request.assert_awaited_once_with("GET", "/version")


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
