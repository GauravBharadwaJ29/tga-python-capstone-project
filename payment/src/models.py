from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    customer_id = Column(Integer, index=True)
    amount = Column(Numeric(10, 2))
    status = Column(String, default="pending")
    payment_method = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("PaymentItem", backref="payment", cascade="all, delete-orphan")

class PaymentItem(Base):
    __tablename__ = "payment_items"
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"))
    product_id = Column(String)
    quantity = Column(Integer)
    price = Column(Float)

# Pydantic models

class PaymentItemSchema(BaseModel):
    product_id: str
    quantity: int
    price: float

    model_config = {"from_attributes": True}  # Pydantic v2 style

class PaymentIn(BaseModel):
    order_id: int
    customer_id: int
    amount: float
    payment_method: str
    items: List[PaymentItemSchema]

    model_config = {"from_attributes": True}  # Pydantic v2 style

class PaymentUpdate(BaseModel):
    status: Optional[str]
    transaction_id: Optional[str]

    model_config = {"from_attributes": True}  # Pydantic v2 style

class PaymentOut(BaseModel):
    id: int
    order_id: int
    customer_id: int
    amount: float
    status: str
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    created_at: datetime
    items: Optional[List[PaymentItemSchema]] = None

    model_config = {"from_attributes": True}  # Pydantic v2 style
