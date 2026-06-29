from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class CategoryBase(SQLModel):
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    products: List["Product"] = Relationship(back_populates="category")

class ProductBase(SQLModel):
    title: str = Field(index=True)
    description: str
    price: float = Field(default=0.0)
    inventory_count: int = Field(default=0)
    image_url: Optional[str] = None
    category_id: int = Field(foreign_key="category.id")

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship back to the parent category
    category: Optional[Category] = Relationship(back_populates="products")

# Pydantic data transfer schemas for validation
class ProductCreate(ProductBase):
    pass

class ProductUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    inventory_count: Optional[int] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None