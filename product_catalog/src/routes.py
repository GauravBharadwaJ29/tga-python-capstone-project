from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from .models import Product, ProductUpdate
from .kafka_producer import kafka
from .utils import custom_error
from bson import ObjectId
from .database import get_db
from .logger_config import logger
from .config import EVENT_PRODUCT_CREATED, EVENT_PRODUCT_UPDATED, EVENT_PRODUCT_DELETED 

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint that verifies MongoDB and Kafka connections"""
    try:
        # Check MongoDB
        await db.command('ping')
        # Check Kafka
        if not kafka.producer:
            await kafka.start()
        logger.debug("Health check passed")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: Product, collection=Depends(get_db)):
    product_dict = product.dict(by_alias=True)
    result = await collection.insert_one(product_dict)
    product_dict["_id"] = str(result.inserted_id)
    await kafka.send_event({"event": EVENT_PRODUCT_CREATED, "product": product_dict})
    return product_dict

@router.get("/products", response_model=list[Product])
async def list_products(collection=Depends(get_db)):
    products = []
    async for p in collection.find():
        p["_id"] = str(p["_id"])
        products.append(p)
    return products

@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str, collection=Depends(get_db)):
    try:
        obj_id = ObjectId(product_id)
    except Exception:
        return custom_error("Invalid product ID", 400)
    product = await collection.find_one({"_id": obj_id})
    if not product:
        return custom_error("Product not found", 404)
    product["_id"] = str(product["_id"])
    return product

@router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, update: ProductUpdate, collection=Depends(get_db)):
    try:
        obj_id = ObjectId(product_id)
    except Exception:
        return custom_error("Invalid product ID", 400)
    result = await collection.update_one(
        {"_id": obj_id}, {"$set": update.dict(exclude_unset=True)}
    )
    if result.matched_count == 0:
        return custom_error("Product not found", 404)
    product = await collection.find_one({"_id": obj_id})
    product["_id"] = str(product["_id"])
    await kafka.send_event({"event": EVENT_PRODUCT_UPDATED, "product": product})
    return product

@router.delete("/products/{product_id}")
async def delete_product(product_id: str, collection=Depends(get_db)):
    try:
        obj_id = ObjectId(product_id)
    except Exception:
        return custom_error("Invalid product ID", 400)
    result = await collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        return custom_error("Product not found", 404)
    await kafka.send_event({"event": EVENT_PRODUCT_DELETED, "product_id": product_id})
    return {"message": "Product deleted"}
