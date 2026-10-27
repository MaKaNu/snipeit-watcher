from fastapi import APIRouter

from snipeit_watcher.services.snipeit_api_client import SnipeitAPIClient

router = APIRouter()
client = SnipeitAPIClient()


@router.post("/users_disabled")
async def users_disabled():
    users = await client.get_disabled_users()
    return {"message": "Execution triggered successfully", "result": users}


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
