from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum



# SQLAlchemy models

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True, nullable=False)
    customer_id = Column(Integer, index=True, nullable=False)
    delivery_address = Column(String, nullable=False)
    status = Column(String, default="pending")
    assigned_to = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    tracking_number = Column(String, nullable=True)
    # Optional: relationship to delivery items (if you want to store line items)
    items = relationship("DeliveryItem", backref="delivery", cascade="all, delete-orphan")

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"    

class DeliveryItem(Base):
    __tablename__ = "delivery_items"
    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id", ondelete="CASCADE"))
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)  # Use Float if needed

# Pydantic models

class DeliveryItemSchema(BaseModel):
    product_id: str
    quantity: int
    price: float

    model_config = {"from_attributes": True}  # Pydantic v2 style

class DeliveryIn(BaseModel):
    order_id: int
    customer_id: int
    delivery_address: str
    items: Optional[List[DeliveryItemSchema]] = None

    model_config = {"from_attributes": True}  # Pydantic v2 style

class DeliveryUpdate(BaseModel):
    status: Optional[str]
    assigned_to: Optional[str]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    tracking_number: Optional[str]

    model_config = {"from_attributes": True}  # Pydantic v2 style

# class DeliveryOut(BaseModel):
#     id: int
#     order_id: int
#     customer_id: int
#     delivery_address: str
#     status: str
#     assigned_to: Optional[str]
#     created_at: datetime
#     shipped_at: Optional[datetime]
#     delivered_at: Optional[datetime]
#     tracking_number: Optional[str]
#     items: Optional[List[DeliveryItemSchema]] = None

#     model_config = {"from_attributes": True}  # Pydantic v2 style

class DeliveryOut(BaseModel):
    id: int
    order_id: int
    customer_id: int
    delivery_address: str
    status: str
    assigned_to: Optional[str]
    created_at: datetime
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    tracking_number: Optional[str] = None
    items: Optional[List[DeliveryItemSchema]] = None

    model_config = {"from_attributes": True}

