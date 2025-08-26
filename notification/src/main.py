from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from contextlib import asynccontextmanager
import os
from .redis_queue import queue 

# queue = RedisQueue()


from .routes import router
from .logger_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting up notification service...")
    await queue.connect()
    logger.info("Queue connected.")
    yield
    # Shutdown logic
    if getattr(queue, "redis", None):
        await queue.redis.close()
        logger.info("Redis connection closed.")
    logger.info("Service shutdown complete.")

app = FastAPI(
    title="Notification Service",
    description="Queues email notifications in Redis and logs metadata in MongoDB.",
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error on {request.method} {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

app.include_router(router)
logger.info(f"FastAPI application initialized for {os.getenv('SERVICE_NAME', 'notification')}")
