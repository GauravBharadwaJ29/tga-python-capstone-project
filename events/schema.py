from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class BaseEvent(BaseModel):
    event_id: str
    timestamp: datetime
    request_id: str
    service: str
    version: str = "1.0"

class StoreEvent(BaseEvent):
    event_type: str  # created, updated, deleted
    store_id: str
    data: Dict[str, Any]

class OrderEvent(BaseEvent):
    event_type: str
    order_id: str
    data: Dict[str, Any]

class InventoryEvent(BaseEvent):
    event_type: str
    product_id: str
    quantity: int
    data: Dict[str, Any]

class PaymentEvent(BaseEvent):
    event_type: str
    payment_id: str
    order_id: str
    data: Dict[str, Any]
