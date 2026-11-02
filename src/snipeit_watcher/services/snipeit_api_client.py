import logging

import httpx

from snipeit_watcher.config import settings
from snipeit_watcher.models import AssetManager, SnipeAssets, SnipeHistories, SnipeUser, SnipeUsers

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

    async def get_user(self, user_id: int) -> SnipeUser:
        return SnipeUser.model_validate(await self._request("GET", f"users/{user_id}"))

    async def get_user_assets(self, user_id: int) -> SnipeAssets:
        endpoint = f"users/{user_id}/assets"
        user_assets = SnipeAssets.model_validate(await self._request("GET", endpoint))
        return user_assets

    async def get_histories(self, asset_id):
        endpoint = f"hardware/{asset_id}/history"
        params = {"sort": "created_at", "order": "desc"}
        histories = SnipeHistories.model_validate(
            await self._request("GET", endpoint, params=params)
        )
        histories.by_action("checkout")

        return histories

    async def get_asset_managers(
        self, user: SnipeUser, managers_by_id: dict[int, AssetManager] | None = None
    ) -> dict[int, AssetManager]:
        """Group a user's assets by the manager who last checked them out.

        Pass `managers_by_id` to accumulate results across several users.
        """
        user_assets = await self.get_user_assets(user.id)

        if managers_by_id is None:
            managers_by_id = {}
        for asset in user_assets.rows:
            # users/{id}/assets omits assigned_to, but the owner is known here.
            asset.assigned_to = user
            histories = await self.get_histories(asset.id)
            if not histories.rows:
                continue

            # Since we already sorted via api request we know that
            # the first entry of histories is always the latest checkout.
            # Actually we hope this is true. XDXDXDXD
            manager_id = histories.rows[0].created_by.id
            if manager_id not in managers_by_id:
                # History's created_by lacks email, so fetch the full user once.
                managers_by_id[manager_id] = AssetManager(
                    asset_manager=await self.get_user(manager_id),
                    assets=[],
                )
            managers_by_id[manager_id].assets.append(asset)

        return managers_by_id
