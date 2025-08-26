from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    status = Column(String, default="pending")
    onboarded_at = Column(DateTime, nullable=True)  # <-- FIXED

# Pydantic models

class StoreIn(BaseModel):
    name: str
    address: str
    contact_email: EmailStr
    contact_phone: str

class StoreUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    contact_email: Optional[EmailStr]
    contact_phone: Optional[str]
    status: Optional[str]

class StoreOut(BaseModel):
    id: int
    name: str
    address: str
    contact_email: EmailStr
    contact_phone: str
    status: str
    onboarded_at: Optional[datetime] = None  # <-- FIXED

    model_config = {"from_attributes": True}  # Pydantic v2 style

# If you want to support onboarding with initial catalog (multi-item)
class ProductItem(BaseModel):
    name: str
    description: Optional[str]
    price: float
    category: str
    stock: int

class StoreOnboardingIn(BaseModel):
    name: str
    address: str
    contact_email: EmailStr
    contact_phone: str
    catalog: Optional[List[ProductItem]] = None
