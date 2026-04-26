"""
Main Module
"""

import asyncio
from typing import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, WebSocketException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError
from starlette.middleware.sessions import SessionMiddleware
from brotli_asgi import BrotliMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from api.utils.task_logger import create_logger
from api.core.config import settings
from api.database.sql_database import sql_database
from api.core.error_handlers import (
    exception,
    http_exception,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    redis_exception_handler,
    ratelimit_exception_handler,
    websocket_exception_handler,
)
from api.route.v1 import api_version_one
from api.core.middlewares import RequestLoggerMiddleware
from api.utils.keepalive_loop import keepalive_loop

logger = create_logger("Main App")

LIMITER = Limiter(key_func=get_remote_address, storage_uri=(settings.redis_url))

PER_MINUTE = "20/minute"
PER_SECOND = "1/second"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    App instance lifspan
    """
    logger.info(msg="Starting Application")

    # Setup background keepalive
    stop_event = asyncio.Event()
    task = asyncio.create_task(keepalive_loop(stop_event=stop_event))
    app.state.keepalive_loop = task
    app.state.stop_event = stop_event

    try:
        yield
    finally:
        logger.info(msg="Shutting Down Application")
        stop_event.set()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        await sql_database.async_engine.dispose(close=False)


app = FastAPI(
    lifespan=lifespan,
    debug=True,
    title="StartInbox.",
    description="StartInbox API Documentation.",
    version="1.0.0",
    terms_of_service=f"{settings.client_side_url}/privacy-policy",
)

origins = [
    settings.client_side_url,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods="*",
    allow_headers="*",
)

app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.secrets)
app.add_middleware(
    BrotliMiddleware, minimum_size=500
)  # compress response larger than 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)


app.include_router(api_version_one)


@app.get("/", tags=["HOME"])
@LIMITER.limit(PER_MINUTE)
@LIMITER.limit(PER_SECOND)
async def read_root(request: Request) -> dict:
    """
    Read root
    """
    return {"message": "Welcome to STARTINBOX API"}


@app.get("/api/v1/health", tags=["HEALTH"], status_code=200)
@LIMITER.limit("20")
@LIMITER.limit("5")
async def health(request: Request):
    """
    Check health
    """
    return {"status": "ok"}


app.add_exception_handler(RateLimitExceeded, ratelimit_exception_handler)
app.add_exception_handler(HTTPException, http_exception)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(RedisError, redis_exception_handler)
app.add_exception_handler(RedisError, ratelimit_exception_handler)
app.add_exception_handler(WebSocketException, websocket_exception_handler)
app.add_exception_handler(Exception, exception)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=int(settings.port or 7000),
        reload=True,
        timeout_keep_alive=60,
    )
