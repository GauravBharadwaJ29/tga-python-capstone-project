import os
from .logger_config import logger

try:
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise ValueError("MONGO_URI environment variable is required")

    MONGO_DB = os.getenv("MONGO_DB")
    if not MONGO_DB:
        raise ValueError("MONGO_DB environment variable is required")
    
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
    if not MONGO_COLLECTION:
        raise ValueError("MONGO_COLLECTION environment variable is required")

    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not KAFKA_BOOTSTRAP_SERVERS:
        raise ValueError("KAFKA_BOOTSTRAP_SERVERS environment variable is required")

    PRODUCT_TOPIC = os.getenv("PRODUCT_TOPIC")
    if not PRODUCT_TOPIC:
        raise ValueError("PRODUCT_TOPIC environment variable is required")
    
    EVENT_PRODUCT_CREATED = os.getenv("EVENT_PRODUCT_CREATED")
    if not EVENT_PRODUCT_CREATED:
        raise ValueError("EVENT_PRODUCT_CREATED environment variable is required")
    
    EVENT_PRODUCT_UPDATED = os.getenv("EVENT_PRODUCT_UPDATED")
    if not EVENT_PRODUCT_UPDATED:
        raise ValueError("EVENT_PRODUCT_UPDATED environment variable is required")
    
    EVENT_PRODUCT_DELETED = os.getenv("EVENT_PRODUCT_DELETED")
    if not EVENT_PRODUCT_DELETED:
        raise ValueError("EVENT_PRODUCT_DELETED environment variable is required")

    PORT = int(os.getenv("PORT"))
    KAFKA_RETRY_COUNT = int(os.getenv("KAFKA_RETRY_COUNT", "10"))
    KAFKA_RETRY_DELAY = int(os.getenv("KAFKA_RETRY_DELAY", "5"))
    SERVICE_NAME = os.getenv("SERVICE_NAME", "default_service")

    logger.info("Configuration loaded successfully")
except ValueError as e:
    logger.error(f"Configuration error: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error loading configuration: {str(e)}")
    raise

class ErrorMessages:
    KAFKA_CONNECTION_FAILED = "Failed to connect to Kafka after {} attempts"
    DATABASE_CONNECTION_FAILED = "Failed to connect to MongoDB: {}"
    PRODUCT_NOT_FOUND = "Product not found"
    INVALID_PRODUCT_ID = "Invalid product ID"
    HEALTH_CHECK_FAILED = "Service health check failed: {}"
    KAFKA_EVENT_FAILED = "Failed to send event to Kafka: {}"
    DB_QUERY_FAILED = "Database query failed: {}"
