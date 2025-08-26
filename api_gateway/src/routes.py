from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import Response
from .config import Config
from .logger_config import logger
from .security import verify_api_key
import uuid
import time
from httpx import AsyncClient
from .utils import custom_error

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    logger.debug("Health check endpoint called")
    return {"status": "ok"}

async def proxy_request(request: Request, service_url: str):
    try:
        request_id = str(uuid.uuid4())
        logger.info(f"Request {request_id}: Proxying to {service_url}{request.url.path}")

        start_time = time.time()
        async with AsyncClient() as client:
            url = f"{service_url}{request.url.path}"
            headers = dict(request.headers)
            headers.pop("x-api-key", None)  # Remove API key before forwarding

            response = await client.request(
                request.method,
                url,
                headers=headers,
                content=await request.body(),
                params=dict(request.query_params)
            )

            duration = time.time() - start_time
            logger.info(f"Request {request_id}: Completed in {duration:.2f}s with status {response.status_code}")
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    except Exception as e:
        logger.error(f"Request {request_id}: Failed - {str(e)}")
        return custom_error("Service unavailable", 503)

def make_proxy_handler(service_url):
    async def handler(request: Request):
        return await proxy_request(request, service_url)
    return handler

# Define your service-to-path mapping here
service_paths = {
    "product": "/products",
    "inventory": "/inventory",
    "order": "/orders",
    "payment": "/payments",
    "billing": "/bills",
    "delivery": "/deliveries",
    "notification": "/notify",
    "store": "/stores",  
}

# Dynamically create routes for each service
# for service, path in service_paths.items():
#     router.add_api_route(
#         f"{path}{{path:path}}",
#         endpoint=make_proxy_handler(Config.Services.get_service_url(service)),
#         methods=["GET", "POST", "PUT", "DELETE"],
#         dependencies=[Depends(verify_api_key)]
#     )
for service, path in service_paths.items():
    # Add explicit base path
    router.add_api_route(
        path,
        endpoint=make_proxy_handler(Config.Services.get_service_url(service)),
        methods=["GET", "POST"],
        dependencies=[Depends(verify_api_key)]
    )
    # Add catch-all for subpaths
    router.add_api_route(
        f"{path}/{{path:path}}",
        endpoint=make_proxy_handler(Config.Services.get_service_url(service)),
        methods=["GET", "POST", "PUT", "DELETE"],
        dependencies=[Depends(verify_api_key)]
    )



    # --- Add explicit auth routes here ---
auth_service_url = Config.Services.get_service_url("auth")
router.add_api_route(
    "/signup",
    endpoint=make_proxy_handler(auth_service_url),
    methods=["POST"],
    dependencies=[]
)
router.add_api_route(
    "/login",
    endpoint=make_proxy_handler(auth_service_url),
    methods=["POST"],
    dependencies=[]
)
router.add_api_route(
    "/me",
    endpoint=make_proxy_handler(auth_service_url),
    methods=["GET"],
    dependencies=[]
)
# --- End auth routes ---


# @router.get("/products")
# async def get_products(request: Request):
#     logger.debug(f"Received GET /products from {request.client.host}")
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(Config.Services.PRODUCT_URL + "/products")
#             response.raise_for_status()
#             logger.info("Successfully fetched products from product_catalog service")
#             return response.json()
#     except httpx.HTTPStatusError as exc:
#         logger.error(f"Error fetching products: {exc.response.status_code} {exc.response.text}")
#         raise HTTPException(status_code=exc.response.status_code, detail="Error fetching products")
#     except Exception as exc:
#         logger.error(f"Unexpected error fetching products: {exc}")
#         raise HTTPException(status_code=500, detail="Internal server error")
