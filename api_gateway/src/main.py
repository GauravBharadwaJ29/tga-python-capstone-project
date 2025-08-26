from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .config import Config
from .logger_config import logger
import os

app = FastAPI(
    title="API Gateway",
    description="Central entry point for all APIs. Handles routing and API key security.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        f"Validation error for request {request.method} {request.url}: {exc.errors()} | Body: {await request.body()}"
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

logger.info(f"API Gateway initialized on port {Config.Server.PORT}")
