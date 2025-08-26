import os
from .logger_config import logger

try:
    POSTGRES_URI = os.getenv("POSTGRES_URI")
    if not POSTGRES_URI:
        raise ValueError("POSTGRES_URI environment variable is required")

    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not KAFKA_BOOTSTRAP_SERVERS:
        raise ValueError("KAFKA_BOOTSTRAP_SERVERS environment variable is required")

    DELIVERY_TOPIC = os.getenv("DELIVERY_TOPIC")
    if not DELIVERY_TOPIC:
        raise ValueError("DELIVERY_TOPIC environment variable is required")
    
    NOTIFICATION_TOPIC=os.getenv("NOTIFICATION_TOPIC")
    if not NOTIFICATION_TOPIC:
        raise ValueError("NOTIFICATION_TOPIC environment variable is required")    
    
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    if not KAFKA_BOOTSTRAP_SERVERS:
        raise ValueError("KAFKA_BOOTSTRAP_SERVERS environment variable is required")    
        
    ORDER_TOPIC = os.getenv("ORDER_TOPIC", "order_events")
    if not ORDER_TOPIC:
        raise ValueError("ORDER_TOPIC environment variable is required")   
        
    PAYMENT_TOPIC = os.getenv("PAYMENT_TOPIC", "payment_events")
    if not PAYMENT_TOPIC:
        raise ValueError("PAYMENT_TOPIC environment variable is required")   
        
    NOTIFICATION_TOPIC = os.getenv("NOTIFICATION_TOPIC", "notification_events")
    if not NOTIFICATION_TOPIC:
        raise ValueError("NOTIFICATION_TOPIC environment variable is required")    
     
    CONSUMER_DELIVERY_GROUP = os.getenv("CONSUMER_DELIVERY_GROUP", "delivery_group")  
    if not CONSUMER_DELIVERY_GROUP:
        raise ValueError("CONSUMER_DELIVERY_GROUP environment variable is required")        
    
    EVENT_DELIVERY_CREATED = os.getenv("EVENT_DELIVERY_CREATED")
    if not EVENT_DELIVERY_CREATED:
        raise ValueError("EVENT_DELIVERY_CREATED environment variable is required")
    
    EVENT_DELIVERY_CANCELLED = os.getenv("EVENT_DELIVERY_CANCELLED")  
    if not EVENT_DELIVERY_CANCELLED:
        raise ValueError("EVENT_DELIVERY_CANCELLED environment variable is required")
    
    EVENT_DELIVERY_DELETED = os.getenv("EVENT_DELIVERY_DELETED")
    if not EVENT_DELIVERY_DELETED:
        raise ValueError("EVENT_DELIVERY_DELETED environment variable is required")
    
    EVENT_DELIVERY_UPDATED = os.getenv("EVENT_DELIVERY_UPDATED")
    if not EVENT_DELIVERY_UPDATED:
        raise ValueError("EVENT_DELIVERY_UPDATED environment variable is required")

    EVENT_PAYMENT_SUCCESSFUL = os.getenv("EVENT_PAYMENT_SUCCESSFUL")
    if not EVENT_PAYMENT_SUCCESSFUL:
        raise ValueError("EVENT_PAYMENT_SUCCESSFUL environment variable is required")    
    
    EVENT_ORDER_CANCELLED = os.getenv("EVENT_ORDER_CANCELLED")
    if not EVENT_ORDER_CANCELLED:
        raise ValueError("EVENT_ORDER_CANCELLED environment variable is required")   
    
    EVENT_ORDER_DELETED = os.getenv("EVENT_ORDER_DELETED")
    if not EVENT_ORDER_DELETED:
        raise ValueError("EVENT_ORDER_DELETED environment variable is required") 

    EVENT_PAYMENT_REFUNDED = os.getenv("EVENT_PAYMENT_REFUNDED")
    if not EVENT_PAYMENT_REFUNDED:
        raise ValueError("EVENT_PAYMENT_REFUNDED environment variable is required")         
    
    

    PORT = int(os.getenv("PORT", "8000"))
    SERVICE_NAME = os.getenv("SERVICE_NAME", "default_service")

    logger.info("Configuration loaded successfully")
except ValueError as e:
    logger.error(f"Configuration error: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error loading configuration: {str(e)}")
    raise
