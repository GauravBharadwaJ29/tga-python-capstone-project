from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URI, MONGO_DB
from .logger_config import logger  # Missing logger import from logger_config

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]
meta_collection = db.notification_meta

async def log_notification_meta(meta: dict):
    await meta_collection.insert_one(meta)
    logger.info("Successfully inserted notification meta")
