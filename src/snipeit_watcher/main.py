import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from snipeit_watcher.api.routes import router
from snipeit_watcher.scheduler import init_scheduler, scheduler

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(title="SnipeIT Watcher", lifespan=lifespan)

app.include_router(router)
