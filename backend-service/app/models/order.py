from enum import Enum
from sqlmodel import SQLModel,Field,Relationship
from typing import List,Optional
from datetime import datetime

#=========OREDER STRICT STATUS========

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"
#=========CART SCHEMA==================

class CartBase(SQLModel):
    product_id:int=Field(foreign_key="product.id")
    quantity:int=Field(default=1)
    
class CartItem(CartBase,table=True):
    id:Optional[int]=Field(primary_key=True,default=None)
    user_id:int=Field(foreign_key="user.id" , index=True)
    created_at:datetime=Field(default_factory=datetime.utcnow)
    
#=========OREDER SCHEMAS===================

class Order(SQLModel,table=True):
    id:Optional[int]=Field(primary_key=True,default=None)
    user_id:int=Field(foreign_key="user.id",index=True)
    total_price:float=Field(default=0.0)
    created_at:datetime=Field(default_factory=datetime.utcnow)
    order_items:Optional[OrderItem]=Relationship(back_populates="order")
    
#========== ORDER SCHEMA TO HISTORY PURPOSE BY SAVING ORDERS IN ORDERITEM==============

class OrderItem(SQLModel,table=True):
    id:Optional[int]=Field(primary_key=True,default=None)
    product_id:int=Field(foreign_key="product.id")
    order_id:int=Field(foreign_key="order.id")
    quantity:int
    price_at_purchase:float
    order:Optional[Order]=Relationship(back_populates="order_items")