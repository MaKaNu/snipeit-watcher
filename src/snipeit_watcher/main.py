from fastapi import FastAPI

from snipeit_watcher.api.routes import router

app = FastAPI(title="SnipeIT Watcher")

app.include_router(router)
