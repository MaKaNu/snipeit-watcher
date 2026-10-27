import logging

import httpx

from snipeit_watcher.config import settings
from snipeit_watcher.models import SnipeUsers

logger = logging.getLogger(__name__)


class SnipeitAPIClient:
    def __init__(self) -> None:
        self.base_url = settings.app_url
        self._client = httpx.AsyncClient(
            base_url=f"{self.base_url}api/v1/",
            timeout=10.0,
            headers={"Authorization": f"Bearer {settings.snipeit_api_token.get_secret_value()}"}
            if settings.snipeit_api_token
            else {},
        )

    async def close(self):
        await self._client.aclose()

    # --- Private Helper Method for API Requests
    async def _request(self, method: str, endpoint: str, **kwargs) -> dict | None:
        """Internal Request method to handle Boilerplate and Error Handling.

        Args:
            method (str): SnipeIT API methods (GET, POST, PATCH, PUT, DEL)
            endpoint (str): Route to the endpoint of the SnipeIT API
            **kargs: Keyword argument forwared to `httpx.AsyncClient.request` (for example, `params` or `json`)

        Returns:
            dict | None: The Json Respnse as dict or None if not available.
        """
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None
        except httpx.HTTPStatusError as e:
            logger.exception(f"HTTP error occured: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError:
            logger.exception("Network error occured.")
            raise

    async def get_disabled_users(self) -> SnipeUsers:
        """Fetch disabled users on snipeit instance"""
        endpoint = "users"
        params = {
            "sort": "created_at",
            "order": "desc",
            "activated": "false",
            "all": "false",
        }
        disabled_users = SnipeUsers.model_validate(
            await self._request("GET", endpoint, params=params)
        )
        disabled_users.apply_whitelist(settings.disabled_users_id_whitelist, invert=True)

        return disabled_users
