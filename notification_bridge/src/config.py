import os
from dotenv import load_dotenv

load_dotenv()

REQUIRED_ENV_VARS = [
    "KAFKA_BOOTSTRAP_SERVERS",
    "CONSUMER_BRIDGE_GROUP",
    "NOTIFICATION_API_URL",
    "BILLING_TOPIC",
    "PAYMENT_TOPIC",
    "ORDER_TOPIC",
    "DELIVERY_TOPIC",
    "INVENTORY_TOPIC",
    "PRODUCT_TOPIC",
    "STORE_TOPIC"
]

try:
    # Attempt to load all required environment variables
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            raise RuntimeError(f"{var} environment variable is required")
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    CONSUMER_BRIDGE_GROUP = os.getenv("CONSUMER_BRIDGE_GROUP")
    NOTIFICATION_API_URL = os.getenv("NOTIFICATION_API_URL")
    BILLING_TOPIC   = os.getenv("BILLING_TOPIC")
    PAYMENT_TOPIC   = os.getenv("PAYMENT_TOPIC")
    ORDER_TOPIC     = os.getenv("ORDER_TOPIC")
    DELIVERY_TOPIC  = os.getenv("DELIVERY_TOPIC")
    INVENTORY_TOPIC = os.getenv("INVENTORY_TOPIC")
    PRODUCT_TOPIC   = os.getenv("PRODUCT_TOPIC")
    STORE_TOPIC     = os.getenv("STORE_TOPIC")
except Exception as e:
    raise RuntimeError(f"Configuration error: {e}")

# Optional configs and event names with defaults
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOGGING_CONFIG = os.getenv("LOGGING_CONFIG", "src/logging_config.yaml")
PORT = int(os.getenv("PORT", "8006"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "notification_bridge")

EVENT_PAYMENT_SUCCESSFUL = os.getenv("EVENT_PAYMENT_SUCCESSFUL", "payment_successful")
EVENT_PAYMENT_FAILED = os.getenv("EVENT_PAYMENT_FAILED", "payment_failed")
EVENT_ORDER_SHIPPED = os.getenv("EVENT_ORDER_SHIPPED", "order_shipped")
EVENT_ORDER_DELIVERED = os.getenv("EVENT_ORDER_DELIVERED", "order_delivered")
# Add more event types as needed
