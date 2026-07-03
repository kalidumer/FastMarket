from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

class CategoryBase(SQLModel):
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    
class Category(CategoryBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    
    products: List["Product"] = Relationship(back_populates="category_rel")
    
class ProductBase(SQLModel):
    title: str = Field(index=True)
    description: str
    price: float = Field(default=0.0)
    inventory_count: int = Field(default=0)
    image_url: Optional[str] = None
    category: int = Field(foreign_key="category.id") 
    
class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    category_rel: Optional[Category] = Relationship(back_populates="products")
    
class ProductCreate(ProductBase):
    pass

class ProductUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    inventory_count: Optional[int] = None
    image_url: Optional[str] = None
    category: Optional[int] = None