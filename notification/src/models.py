from pydantic import BaseModel
from typing import List
from pydantic import BaseModel
from typing import List

class NotificationItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class NotificationIn(BaseModel):
    to: str
    subject: str
    items: List[NotificationItem]

class OrderNotification(BaseModel):
    order_id: int
    customer_name: str
    items: List[NotificationItem]
    delivery_address: str

class PaymentNotification(BaseModel):
    order_id: int
    amount: float
    status: str

class DeliveryNotification(BaseModel):
    order_id: int
    status: str
    assigned_to: str
