import logging

from fastapi import APIRouter

from snipeit_watcher.services.snipeit_api_client import SnipeitAPIClient

logger = logging.getLogger(__name__)

router = APIRouter()
client = SnipeitAPIClient()


@router.post("/users_disabled")
async def users_disabled():
    users = await client.get_disabled_users()
    return {"message": "Execution triggered successfully", "result": users}


@router.get("/health")
async def health_check():
    try:
        version = await client._request("GET", "/version")
        logger.debug(version)
    except Exception as e:
        return {
            "status": {
                "snipeit_con": f"unhealthy {e}",
                "watcher_con": "healthy",
            }
        }
    else:
        return {
            "status": {
                "snipeit_con": "healthy",
                "watcher_con": "healthy",
            }
        }
