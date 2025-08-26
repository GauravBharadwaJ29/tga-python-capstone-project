import os
from .logger_config import logger

try:
    POSTGRES_URI = os.getenv("POSTGRES_URI")
    if not POSTGRES_URI:
        raise ValueError("POSTGRES_URI environment variable is required")

    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not KAFKA_BOOTSTRAP_SERVERS:
        raise ValueError("KAFKA_BOOTSTRAP_SERVERS environment variable is required")

    INVENTORY_TOPIC = os.getenv("INVENTORY_TOPIC")
    if not INVENTORY_TOPIC:
        raise ValueError("INVENTORY_TOPIC environment variable is required")

    ORDER_TOPIC = os.getenv("ORDER_TOPIC")
    if not ORDER_TOPIC:
        raise ValueError("ORDER_TOPIC environment variable is required")
    

    CONSUMER_INVENTORY_GROUP = os.getenv("CONSUMER_INVENTORY_GROUP")
    if not CONSUMER_INVENTORY_GROUP:
        raise ValueError("CONSUMER_INVENTORY_GROUP environment variable is required")    
    
    EVENT_ORDER_CREATED= os.getenv("EVENT_ORDER_CREATED")
    if not EVENT_ORDER_CREATED:
        raise ValueError("EVENT_ORDER_CREATED environment variable is required")
    
    EVENT_ORDER_FAILED= os.getenv("EVENT_ORDER_FAILED")
    if not EVENT_ORDER_FAILED:
        raise ValueError("EVENT_ORDER_FAILED environment variable is required")
    
    EVENT_PAYMENT_SUCCESSFUL= os.getenv("EVENT_PAYMENT_SUCCESSFUL")
    if not EVENT_PAYMENT_SUCCESSFUL:
        raise ValueError("EVENT_PAYMENT_SUCCESSFUL environment variable is required")
    
    EVENT_INVENTORY_CREATED= os.getenv("EVENT_INVENTORY_CREATED")
    if not EVENT_INVENTORY_CREATED:
        raise ValueError("EVENT_INVENTORY_CREATED environment variable is required")
    
    EVENT_INVENTORY_UPDATED= os.getenv("EVENT_INVENTORY_UPDATED")
    if not EVENT_INVENTORY_UPDATED:
        raise ValueError("EVENT_INVENTORY_UPDATED environment variable is required")
    
    EVENT_INVENTORY_DELETED= os.getenv("EVENT_INVENTORY_DELETED")
    if not EVENT_INVENTORY_DELETED:
        raise ValueError("EVENT_INVENTORY_DELETED environment variable is required")

    PORT = int(os.getenv("PORT", "8002"))  # Keep default port for development
    SERVICE_NAME = os.getenv("SERVICE_NAME", "default_service")
    logger.info("Configuration loaded successfully")
except ValueError as e:
    logger.error(f"Configuration error: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error loading configuration: {str(e)}")
    raise
