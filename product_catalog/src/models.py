from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    description: Optional[str]
    price: float
    category: str
    stock: int
    store_id: str

class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    category: Optional[str]
    stock: Optional[int]
    store_id: Optional[str]
