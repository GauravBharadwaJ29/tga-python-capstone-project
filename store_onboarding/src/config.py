import os
from .logger_config import logger  # logger_config.py already loads environment variables

try:
    # Required environment variables
    POSTGRES_URI = os.getenv("POSTGRES_URI")
    if not POSTGRES_URI:
        raise ValueError("POSTGRES_URI environment variable is required")

    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not KAFKA_BOOTSTRAP_SERVERS:
        raise ValueError("KAFKA_BOOTSTRAP_SERVERS environment variable is required")

    STORE_TOPIC = os.getenv("STORE_TOPIC")
    if not STORE_TOPIC:
        raise ValueError("STORE_TOPIC environment variable is required")
    
    EVENT_PRODUCT_ONBOARDED=os.getenv("EVENT_PRODUCT_ONBOARDED")
    if not EVENT_PRODUCT_ONBOARDED:
        raise ValueError("EVENT_PRODUCT_ONBOARDED environment variable is required")
    
    EVENT_STORE_ONBOARDED=os.getenv("EVENT_STORE_ONBOARDED")
    if not EVENT_STORE_ONBOARDED:
        raise ValueError("EVENT_STORE_ONBOARDED environment variable is required")

    EVENT_STORE_UPDATED=os.getenv("EVENT_STORE_UPDATED")
    if not EVENT_STORE_UPDATED:
        raise ValueError("EVENT_STORE_UPDATED environment variable is required")    
    
    EVENT_STORE_DELETED=os.getenv("EVENT_STORE_DELETED")
    if not EVENT_STORE_DELETED:
        raise ValueError("EVENT_STORE_DELETED environment variable is required")      


    # Optional environment variables with defaults
    PORT = int(os.getenv("PORT", "8008"))
    KAFKA_RETRY_COUNT = int(os.getenv("KAFKA_RETRY_COUNT", "10"))
    KAFKA_RETRY_DELAY = int(os.getenv("KAFKA_RETRY_DELAY", "5"))
    SQL_DEBUG = os.getenv("SQL_DEBUG", "").lower() == "true"
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
    DATABASE_CONNECTION_FAILED = "Failed to initialize database: {}"
    STORE_NOT_FOUND = "Store not found"
    STORE_CREATE_FAILED = "Failed to create store: {}"
    KAFKA_EVENT_FAILED = "Failed to send event to Kafka: {}"
