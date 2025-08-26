import os
from .logger_config import logger

class Config:
    """API Gateway configuration"""
    SERVICE_NAME = os.getenv("SERVICE_NAME", "default_service")
    
    class Security:
        API_KEY = os.getenv("API_KEY")
        if not API_KEY:
            logger.error("API_KEY environment variable is required")
            raise ValueError("API_KEY environment variable is required")

    class Server:
        PORT = int(os.getenv("PORT", "8080"))
        HOST = os.getenv("HOST", "0.0.0.0")

    class Services:
        PRODUCT_URL = "http://product_catalog:8001"
        INVENTORY_URL = "http://inventory:8002"
        ORDER_URL = "http://order:8003"
        PAYMENT_URL = "http://payment:8004"
        BILLING_URL = "http://billing:8005"
        DELIVERY_URL = "http://delivery:8006"
        NOTIFICATION_URL = "http://notification:8007"
        STORE_URL = "http://store_onboarding:8008"
        AUTH_URL = "http://auth_service:8009"  # <-- Add this line

        @classmethod
        def get_service_url(cls, service_name: str) -> str:
            mapping = {
                "product": cls.PRODUCT_URL,
                "inventory": cls.INVENTORY_URL,
                "order": cls.ORDER_URL,
                "payment": cls.PAYMENT_URL,
                "billing": cls.BILLING_URL,
                "delivery": cls.DELIVERY_URL,
                "notification": cls.NOTIFICATION_URL,
                "store": cls.STORE_URL,
                "auth": cls.AUTH_URL,  # <-- Add this line
            }
            try:
                return mapping[service_name]
            except KeyError:
                raise ValueError(f"Unknown service: {service_name}")

logger.info("Configuration loaded successfully")
