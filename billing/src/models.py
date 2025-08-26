from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class BillingItem(Base):
    __tablename__ = "billing_items"
    id = Column(Integer, primary_key=True, index=True)
    billing_id = Column(Integer, ForeignKey("billing.id", ondelete="CASCADE"))
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    def __repr__(self):
        return f"<BillingItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"    

class Billing(Base):
    __tablename__ = "billing"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True, nullable=False)
    customer_id = Column(Integer, index=True, nullable=False)
    customer_name = Column(String, nullable=True)
    payment_method = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending", nullable=False)
    billing_date  = Column(DateTime, default=datetime.utcnow)
    items = relationship("BillingItem", backref="billing", cascade="all, delete-orphan")  
    deleted = Column(Boolean, default=False, index=True)  # <-- Add this line here
    def __repr__(self):
        return f"<Billing(id={self.id}, order_id={self.order_id}, status={self.status})>"

class BillingAuditLog(Base):
    __tablename__ = "billing_audit_log"
    id = Column(Integer, primary_key=True, index=True)
    billing_id = Column(Integer, ForeignKey("billing.id", ondelete="CASCADE"))
    old_status = Column(String, nullable=False)
    new_status = Column(String, nullable=False)
    changed_by = Column(String, nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f"<BillingAuditLog(id={self.id}, billing_id={self.billing_id}, old_status={self.old_status}, new_status={self.new_status})>"    
# Pydantic models

from datetime import datetime

class BillingAuditLogOut(BaseModel):
    id: int
    billing_id: int
    old_status: str
    new_status: str
    changed_by: str
    changed_at: datetime
    model_config = {"from_attributes": True}  # Pydantic v2 style

class BillItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class BillIn(BaseModel):
    order_id: int
    amount: float
    items: List[BillItem]

class BillUpdate(BaseModel):
    status: Optional[str]   

class BillingItemOut(BaseModel):
    id: int
    product_id: str
    quantity: int
    price: float
    model_config = {"from_attributes": True}  # Pydantic v2 style


class BillingOut(BaseModel):
    id: int
    order_id: int
    customer_id: int
    customer_name: Optional[str] = None
    payment_method: Optional[str] = None
    amount: float
    status: str
    billing_date: datetime
    items: List[BillingItemOut]
    model_config = {"from_attributes": True}  # Pydantic v2 style

