from fastapi import Header, HTTPException, status, Request
from typing import Optional
from .logger_config import logger
from .config import Config

async def verify_api_key(request: Request, x_api_key: Optional[str] = Header(None)):
    if request.method == "OPTIONS":
        logger.debug("Skipping API key verification for OPTIONS request")
        return
        
    if x_api_key != Config.Security.API_KEY:
        logger.warning(f"Invalid API key attempt from {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": 401, "message": "Invalid or missing API key"}}
        )
    logger.debug(f"Valid API key from {request.client.host}")


# Uncomment for future rate limiting
# from starlette.middleware.base import BaseHTTPMiddleware
# class RateLimitMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#         # Implement rate limiting logic here
#         return await call_next(request)
