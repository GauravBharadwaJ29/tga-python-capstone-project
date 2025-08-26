from contextlib import asynccontextmanager
from fastapi import FastAPI
from .logger_config import logger
from .routes import router
from .database import Base, engine
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse  
from fastapi import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Auth Service...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured.")
    # NOTE: For production, use Alembic migrations instead of create_all
    yield
    # (Optional) Add shutdown/cleanup logic here

app = FastAPI(title="Auth Service", lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        f"Validation error for request to {request.url.path}: {exc.errors()} | Body: {await request.body()}"
    )
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Request validation failed. Check your input data."
        },
    )

app.include_router(router)
logger.info(f"FastAPI application initialized for {os.getenv('SERVICE_NAME')}")
