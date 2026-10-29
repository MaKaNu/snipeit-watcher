import os

import httpx
import pytest

BASE_URL = os.getenv("WATCHER_BASE_URL", "http://localhost:8000").rstrip("/")


@pytest.fixture(scope="session")
def stack_base_url():
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=2.0)
    except httpx.RequestError:
        pytest.skip(f"Watcher stack is not reachable at {BASE_URL}")
    response.raise_for_status()
    return BASE_URL


def test_users_disabled_against_stack(stack_base_url):
    response = httpx.post(f"{stack_base_url}/users_disabled", timeout=10.0)
    response.raise_for_status()

    users = response.json()["result"]["rows"]
    usernames = {user["username"] for user in users}

    assert {"bob.disabled", "carol.disabled", "dave.disabled.clean"} <= usernames
