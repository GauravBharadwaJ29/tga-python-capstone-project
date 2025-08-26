import os
from .logger_config import logger

class ErrorMessages:
    REDIS_CONNECTION_ERROR = "Failed to connect to Redis: {}"
    QUEUE_ERROR = "Failed to process notification: {}"
    MONGO_CONNECTION_ERROR = "Failed to connect to MongoDB: {}"

try:
    REDIS_URL = os.getenv("REDIS_URL")
    if not REDIS_URL:
        raise ValueError("REDIS_URL environment variable is required")

    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise ValueError("MONGO_URI environment variable is required")

    MONGO_DB = os.getenv("MONGO_DB")
    if not MONGO_DB:
        raise ValueError("MONGO_DB environment variable is required")

    PORT = int(os.getenv("PORT"))
    QUEUE_NAME = os.getenv("QUEUE_NAME", "notification_queue")
    SERVICE_NAME = os.getenv("SERVICE_NAME", "default_service")

    logger.info("Configuration loaded successfully")
except ValueError as e:
    logger.error(f"Configuration error: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error loading configuration: {str(e)}")
    raise
