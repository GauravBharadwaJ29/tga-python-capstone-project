from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URI, MONGO_DB, MONGO_COLLECTION, ErrorMessages
from .logger_config import logger

try:
    logger.info(f"Connecting to MongoDB at {MONGO_URI}")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    products_collection = db[MONGO_COLLECTION]
    logger.info(f"MongoDB connection established. Using collection: {MONGO_COLLECTION}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise RuntimeError(ErrorMessages.DATABASE_CONNECTION_FAILED.format(str(e)))

async def get_db():
    try:
        # Check MongoDB connection
        await db.command('ping')
        yield db[MONGO_COLLECTION]  # <--- Yield the collection directl
    except Exception as e:
        logger.error(f"Database access error: {str(e)}")
        raise RuntimeError(ErrorMessages.DATABASE_CONNECTION_FAILED.format(str(e)))
    finally:
        # Note: Don't close client here as it's shared
        pass

