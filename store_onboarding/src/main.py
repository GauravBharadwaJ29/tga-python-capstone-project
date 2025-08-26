from contextlib import asynccontextmanager
from fastapi import FastAPI
from .routes import router
from .kafka_producer import kafka
from .logger_config import logger
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse  
from fastapi import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await kafka.start()
    logger.info("Application startup complete")
    yield
    # Shutdown
    await kafka.stop()
    logger.info("Application shutdown complete")
    

app = FastAPI(lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error on {request.method} {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )
@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.exception(f"Unhandled exception: {exc}")
        raise
app.include_router(router)
logger.info(f"FastAPI application initialized for {os.getenv('SERVICE_NAME')}")