from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"


class CartBase(SQLModel):
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=1)
    
class CartItem(CartBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    product_id: int = Field(foreign_key="product.id")
    order_id: int = Field(foreign_key="order.id")
    quantity: int
    price_at_purchase: float
    
    # Changed back_populates to point specifically to order_items
    order: Optional["Order"] = Relationship(back_populates="order_items")

class Payment(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    order_id: int = Field(foreign_key="order.id", index=True)
    txt_ref: str = Field(unique=True, index=True)
    chapa_id: Optional[str] = Field(default=None)   
    amount: float
    method: Optional[str] = Field(default=None)    
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Changed back_populates to point specifically to payments
    order: Optional["Order"] = Relationship(back_populates="payments")

class Order(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id", index=True)
    total_price: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    txt_ref: Optional[str] = Field(default=None, unique=True, index=True)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    
    order_items: List[OrderItem] = Relationship(back_populates="order")
    payments: List[Payment] = Relationship(back_populates="order")