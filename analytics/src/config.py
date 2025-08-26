import os
from .utils import load_environment
from .logger_config import logger

# Load environment with required variables
load_environment([
    'ORDERS_JSONL',
    'PRODUCTS_CSV',
    'STORES_CSV',
    'OUTPUT_DIR'
])

# Add constants for commonly used values
class Config:
    # Paths
    DEFAULT_LOG_DIR = '/var/log/default_service'
    DEFAULT_CONFIG_PATH = 'src/logging_config.yaml'
    
    # File paths
    ORDERS_JSONL = os.getenv("ORDERS_JSONL", "sample_data/orders.jsonl")
    PRODUCTS_CSV = os.getenv("PRODUCTS_CSV", "sample_data/products.csv")
    STORES_CSV = os.getenv("STORES_CSV", "sample_data/stores.csv")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output/")
    SERVICE_NAME = os.getenv("SERVICE_NAME", "default_service")  # Default to 'default_service' if not set

class ColumnNames:
    class Order:
        ID = "id"
        ITEMS = "items"
        CUSTOMER_NAME = "customer_name"
        CUSTOMER_CONTACT = "customer_contact"
        DELIVERY_ADDRESS = "delivery_address"
        STATUS = "status"
        CREATED_AT = "created_at"
        
    class Item:
        ORDER_ID = "order_id"
        PRODUCT_ID = "product_id"
        QUANTITY = "quantity"
        PRICE = "price"

try:
    logger.info("Configuration loaded successfully")
    logger.debug(f"ORDERS_JSONL: {Config.ORDERS_JSONL}")
    logger.debug(f"PRODUCTS_CSV: {Config.PRODUCTS_CSV}")
    logger.debug(f"STORES_CSV: {Config.STORES_CSV}")
    logger.debug(f"OUTPUT_DIR: {Config.OUTPUT_DIR}")
except Exception as e:
    logger.error(f"Error loading configuration: {str(e)}")
    raise