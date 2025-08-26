import os
from .logger_config import logger  # logger_config.py already loads environment variables

try:
    POSTGRES_URI = os.getenv("POSTGRES_URI")
    if not POSTGRES_URI:
        raise ValueError("POSTGRES_URI environment variable is required")

    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not KAFKA_BOOTSTRAP_SERVERS:
        raise ValueError("KAFKA_BOOTSTRAP_SERVERS environment variable is required")

    BILLING_TOPIC = os.getenv("BILLING_TOPIC")
    if not BILLING_TOPIC:
        raise ValueError("BILLING_TOPIC environment variable is required")

    PORT = int(os.getenv("PORT", "8005"))
    SQL_DEBUG = os.getenv("SQL_DEBUG", "").lower() == "true"
    SERVICE_NAME = os.getenv("SERVICE_NAME", "default_service")

    PAYMENT_TOPIC = os.getenv("PAYMENT_TOPIC")
    if not PAYMENT_TOPIC:
        raise ValueError("PAYMENT_TOPIC environment variable is required")

    ORDER_TOPIC = os.getenv("ORDER_TOPIC")
    if not ORDER_TOPIC:
        raise ValueError("ORDER_TOPIC environment variable is required")  

    CONSUMER_BILLING_GROUP = os.getenv("CONSUMER_BILLING_GROUP")
    if not CONSUMER_BILLING_GROUP:
        raise ValueError("CONSUMER_BILLING_GROUP environment variable is required")      
    
    EVENT_PAYMENT_SUCCESSFUL = os.getenv("EVENT_PAYMENT_SUCCESSFUL")
    if not EVENT_PAYMENT_SUCCESSFUL:
        raise ValueError("EVENT_PAYMENT_SUCCESSFUL environment variable is required")
          
    EVENT_PAYMENT_FAILED = os.getenv("EVENT_PAYMENT_FAILED")
    if not EVENT_PAYMENT_FAILED:
        raise ValueError("EVENT_PAYMENT_FAILED environment variable is required")
    
    EVENT_ORDER_CANCELLED = os.getenv("EVENT_ORDER_CANCELLED")
    if not EVENT_ORDER_CANCELLED:
        raise ValueError("EVENT_ORDER_CANCELLED environment variable is required")
    
    EVENT_INVOICE_GENERATED = os.getenv("EVENT_INVOICE_GENERATED")
    if not EVENT_INVOICE_GENERATED:
        raise ValueError("EVENT_INVOICE_GENERATED environment variable is required")
    
    EVENT_INVOICE_FAILED = os.getenv("EVENT_INVOICE_FAILED")
    if not EVENT_INVOICE_FAILED:
        raise ValueError("EVENT_INVOICE_FAILED environment variable is required")
    
    EVENT_INVOICE_CANCELLED = os.getenv("EVENT_INVOICE_CANCELLED")
    if not EVENT_INVOICE_CANCELLED:
        raise ValueError("EVENT_INVOICE_CANCELLED environment variable is required")
    


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
    BILL_NOT_FOUND = "Bill not found"
    BILL_CREATE_FAILED = "Failed to create bill: {}"
