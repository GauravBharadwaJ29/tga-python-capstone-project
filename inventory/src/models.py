from sqlalchemy import Column, Integer, String
from .database import Base
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from datetime import datetime   

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True, nullable=False)
    store_id = Column(Integer, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (UniqueConstraint('product_id', 'store_id'),)

# Pydantic models for API
from pydantic import BaseModel

class InventoryIn(BaseModel):
    product_id: str
    store_id: int
    quantity: int

class InventoryUpdate(BaseModel):
    quantity: int

class InventoryOut(BaseModel):
    id: int
    product_id: str
    store_id: int
    quantity: int

    model_config = {"from_attributes": True}  # Pydantic v2 style
