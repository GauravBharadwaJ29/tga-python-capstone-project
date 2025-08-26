import os
from .logger_config import logger  # logger_config.py already loads environment variables

try:
    POSTGRES_URI = os.getenv("POSTGRES_URI")
    if not POSTGRES_URI:
        raise ValueError("POSTGRES_URI environment variable is required")

    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not KAFKA_BOOTSTRAP_SERVERS:
        raise ValueError("KAFKA_BOOTSTRAP_SERVERS environment variable is required")

    PAYMENT_TOPIC = os.getenv("PAYMENT_TOPIC")
    if not PAYMENT_TOPIC:
        raise ValueError("PAYMENT_TOPIC environment variable is required")
    
    NOTIFICATION_TOPIC=os.getenv("NOTIFICATION_TOPIC")
    if not NOTIFICATION_TOPIC:
        raise ValueError("NOTIFICATION_TOPIC environment variable is required")    
    
    ORDER_TOPIC=os.getenv("ORDER_TOPIC")
    if not ORDER_TOPIC:
        raise ValueError("ORDER_TOPIC environment variable is required")  
    
    CONSUMER_PAYMENT_GROUP=os.getenv("CONSUMER_PAYMENT_GROUP")
    if not ORDER_TOPIC:
        raise ValueError("ORDER_TOPIC environment variable is required")     
    
    EVENT_ORDER_CREATED = os.getenv("EVENT_ORDER_CREATED")
    if not EVENT_ORDER_CREATED:
        raise ValueError("EVENT_ORDER_CREATED environment variable is required")  
    
    EVENT_ORDER_CANCELLED = os.getenv("EVENT_ORDER_CANCELLED")
    if not EVENT_ORDER_CANCELLED:
        raise ValueError("EVENT_ORDER_CANCELLED environment variable is required") 

    EVENT_PAYMENT_SUCCESSFUL = os.getenv("EVENT_PAYMENT_SUCCESSFUL")
    if not EVENT_PAYMENT_SUCCESSFUL:
        raise ValueError("EVENT_PAYMENT_SUCCESSFUL environment variable is required")   
    
    EVENT_PAYMENT_FAILED = os.getenv("EVENT_PAYMENT_FAILED")
    if not EVENT_PAYMENT_FAILED:
        raise ValueError("EVENT_PAYMENT_FAILED environment variable is required")
    
    EVENT_PAYMENT_REFUNDED = os.getenv("EVENT_PAYMENT_REFUNDED")
    if not EVENT_PAYMENT_REFUNDED:
        raise ValueError("EVENT_PAYMENT_REFUNDED environment variable is required")
    
    EVENT_PAYMENT_UPDATED = os.getenv("EVENT_PAYMENT_UPDATED")
    if not EVENT_PAYMENT_UPDATED:
        raise ValueError("EVENT_PAYMENT_UPDATED environment variable is required")
    
    EVENT_PAYMENT_DELETED = os.getenv("EVENT_PAYMENT_DELETED")
    if not EVENT_PAYMENT_DELETED:
        raise ValueError("EVENT_PAYMENT_DELETED environment variable is required")
    
    EVENT_PAYMENT_PROCESSED = os.getenv("EVENT_PAYMENT_DELETED")
    if not EVENT_PAYMENT_DELETED:
        raise ValueError("EVENT_PAYMENT_DELETED environment variable is required")    

    PORT = int(os.getenv("PORT"))
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
    PAYMENT_NOT_FOUND = "Payment not found"
    PAYMENT_CREATE_FAILED = "Failed to create payment: {}"
    KAFKA_EVENT_FAILED = "Failed to send Kafka event: {}"
