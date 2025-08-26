import os
from .logger_config import logger

try:
    POSTGRES_URI = os.getenv("POSTGRES_URI")
    if not POSTGRES_URI:
        raise ValueError("POSTGRES_URI environment variable is required")

    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not KAFKA_BOOTSTRAP_SERVERS:
        raise ValueError("KAFKA_BOOTSTRAP_SERVERS environment variable is required")

    ORDER_TOPIC = os.getenv("ORDER_TOPIC")
    if not ORDER_TOPIC:
        raise ValueError("ORDER_TOPIC environment variable is required")
    
    INVENTORY_TOPIC = os.getenv("INVENTORY_TOPIC")
    if not INVENTORY_TOPIC:
        raise ValueError("INVENTORY_TOPIC environment variable is required")
    
    NOTIFICATION_TOPIC = os.getenv("NOTIFICATION_TOPIC")
    if not NOTIFICATION_TOPIC:
        raise ValueError("NOTIFICATION_TOPIC environment variable is required") 
    
    PAYMENT_TOPIC = os.getenv("PAYMENT_TOPIC")
    if not PAYMENT_TOPIC:
        raise ValueError("PAYMENT_TOPIC environment variable is required")   
    
    CONSUMER_ORDER_GROUP = os.getenv("CONSUMER_ORDER_GROUP")
    if not CONSUMER_ORDER_GROUP:
        raise ValueError("CONSUMER_ORDER_GROUP environment variable is required")
    
    EVENT_ORDER_CREATED = os.getenv("EVENT_ORDER_CREATED")
    if not EVENT_ORDER_CREATED:
        raise ValueError("EVENT_ORDER_CREATED environment variable is required")
    
    EVENT_ORDER_CANCELLED = os.getenv("EVENT_ORDER_CANCELLED")
    if not EVENT_ORDER_CANCELLED:
        raise ValueError("EVENT_ORDER_CANCELLED environment variable is required")
    
    EVENT_ORDER_UPDATED = os.getenv("EVENT_ORDER_UPDATED")
    if not EVENT_ORDER_UPDATED:
        raise ValueError("EVENT_ORDER_UPDATED environment variable is required")
    
    EVENT_ORDER_DELETED = os.getenv("EVENT_ORDER_DELETED")
    if not EVENT_ORDER_DELETED: 
        raise ValueError("EVENT_ORDER_DELETED environment variable is required")

    EVENT_ORDER_FAILED = os.getenv("EVENT_ORDER_FAILED")
    if not EVENT_ORDER_FAILED: 
        raise ValueError("EVENT_ORDER_FAILED environment variable is required")
    
    EVENT_ORDER_FAILED_NOTIFICATION=os.getenv("EVENT_ORDER_FAILED_NOTIFICATION")
    if not EVENT_ORDER_FAILED_NOTIFICATION: 
        raise ValueError("EVENT_ORDER_FAILED_NOTIFICATION environment variable is required")  

    EVENT_PAYMENT_FAILED=os.getenv("EVENT_PAYMENT_FAILED")
    if not EVENT_PAYMENT_FAILED: 
        raise ValueError("EVENT_PAYMENT_FAILED environment variable is required")
    
    EVENT_PAYMENT_SUCCESSFUL=os.getenv("EVENT_PAYMENT_SUCCESSFUL")
    if not EVENT_PAYMENT_SUCCESSFUL: 
        raise ValueError("EVENT_PAYMENT_SUCCESSFUL environment variable is required")    

    PORT = int(os.getenv("PORT"))
    MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "10"))
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
    ORDER_NOT_FOUND = "Order not found"
    ORDER_CREATE_FAILED = "Failed to create order: {}"
