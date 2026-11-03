import logging

from fastapi import APIRouter

from snipeit_watcher.services.snipeit_api_client import SnipeitAPIClient

logger = logging.getLogger(__name__)

router = APIRouter()
client = SnipeitAPIClient()


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
