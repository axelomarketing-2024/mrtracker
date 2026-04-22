from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import config
import scheduler
import webhook


@asynccontextmanager
async def lifespan(app: FastAPI):
    config.validate()
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(webhook.router)


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})
