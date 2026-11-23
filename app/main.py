import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import humidity_router, pressure_router, temperature_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="数据采集演示后台", version="0.1.0", lifespan=lifespan)

for r in (temperature_router, humidity_router, pressure_router):
    app.include_router(r)


@app.get("/health", tags=["系统"])
def health():
    return {"status": "ok"}
