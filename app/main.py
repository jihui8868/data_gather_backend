import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError

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


logger = logging.getLogger(__name__)


@app.exception_handler(RequestValidationError)
async def log_validation_error(request: Request, exc: RequestValidationError):
    logger.warning(
        "请求校验失败 %s %s query=%s payload=%s errors=%s",
        request.method,
        request.url.path,
        request.url.query or "-",
        exc.body,
        exc.errors(),
    )
    return await request_validation_exception_handler(request, exc)


@app.get("/health", tags=["系统"])
def health():
    return {"status": "ok"}
