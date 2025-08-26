from contextlib import asynccontextmanager
from fastapi import FastAPI
from .routes import router
from .kafka_producer import kafka
from .logger_config import logger
import os
from .kafka_consumer import kafka_consumer
import asyncio
from typing import AsyncGenerator
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse  
from fastapi import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        await kafka.start()
        logger.info("Kafka producer started")
        consumer_task = asyncio.create_task(kafka_consumer.consume())
        logger.info("Kafka consumer background task started")
        yield
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    finally:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Kafka consumer background task cancelled")
        except Exception as e:
            logger.error(f"Kafka consumer shutdown error: {e}")
        await kafka.stop()
        logger.info("Kafka producer stopped")

app = FastAPI(
    title=os.getenv('SERVICE_NAME', 'Delivery Service'),
    description="Manages delivery assignments and status. Publishes events to Kafka.",
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
logger.info(f"FastAPI application initialized for {os.getenv('SERVICE_NAME')}")

