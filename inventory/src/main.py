from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from .routes import router

from .logger_config import logger
from .kafka_producer import kafka
from .kafka_consumer import kafka_consumer
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse  
from fastapi import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Kafka producer
    await kafka.start()
    logger.info("Kafka producer started")

    # Start the Kafka consumer as a background task
    consumer_task = asyncio.create_task(kafka_consumer.consume())
    logger.info("Kafka consumer background task started")
    try:
        yield  # Application runs here
    finally:
        # Shutdown sequence
        # On shutdown, cancel the consumer task
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Kafka consumer background task cancelled")

       # Stop Kafka producer
        await kafka.stop()
        logger.info("Kafka producer stopped")

app = FastAPI(
    title="Inventory Service",
    description="Manages product inventory. Publishes and consumes events via Kafka.",
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