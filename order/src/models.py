from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import List
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Numeric

from typing import Optional

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_contact = Column(String)
    delivery_address = Column(String)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    store_id = Column(Integer) # <--- ADD THIS LINE
    items = relationship("OrderItem", backref="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

from typing import Optional
from pydantic import BaseModel

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    delivery_address: Optional[str] = None
    amount: Optional[float] = None
    payment_method: Optional[str] = None
    # Add more fields if you want to allow updating them


# Pydantic models

class OrderItemIn(BaseModel):
    product_id: str
    quantity: int
    price: float


class OrderIn(BaseModel):
    customer_id: int
    customer_name: str
    customer_contact: str
    delivery_address: str
    amount: float
    payment_method: str    
    store_id: int   
    items: List[OrderItemIn]

class OrderItemOut(BaseModel):
    product_id: str
    quantity: int
    price: float


class OrderOut(BaseModel):
    id: int
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    delivery_address: Optional[str] = None
    amount: Optional[float] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    store_id: Optional[int] = None
    items: List[OrderItemOut]
    model_config = {"from_attributes": True}

# class OrderOut(BaseModel):
#     id: int
#     customer_id: int
#     customer_name: str
#     customer_contact: str
#     delivery_address: str
#     amount: float
#     payment_method: str
#     status: str
#     created_at: datetime
#     store_id: int # <--- ADD THIS LINE to the output model
#     items: List[OrderItemOut]
#     model_config = {"from_attributes": True}  # Pydantic v2 style

class OrderUpdate(BaseModel):
    status: Optional[str]
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    delivery_address: Optional[str] = None
    amount: Optional[float] = None
    payment_method: Optional[str] = None
