from unittest.mock import AsyncMock, MagicMock

import httpx
from fastapi.testclient import TestClient

from snipeit_watcher import main as main_module
from snipeit_watcher.api.routes import client as route_client
from snipeit_watcher.main import app

client = TestClient(app)


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
            "snipeit_con": "unhealthy",
            "watcher_con": "healthy",
        }
    }
    request.assert_awaited_once_with("GET", "/version")


def test_lifespan_starts_and_stops_scheduler(monkeypatch):
    scheduler = MagicMock()
    monkeypatch.setattr(main_module, "init_scheduler", lambda: scheduler)

    with TestClient(app):
        scheduler.shutdown.assert_not_called()
    scheduler.shutdown.assert_called_once_with()
