from fastapi import HTTPException,APIRouter,status,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from  app.models.order import (CartItem,CartBase,Order,OrderItem,OrderStatus)
from app.core.auth_guard import get_current_user
from app.core.database import get_session
from app.models.user import User
from app.models.product import Product


router=APIRouter(prefix="/api/order",tags=["Order Management Related"])

@router.post("/cart",response_model=CartItem)
async def add_to_cart(
    payload:CartBase,
    session:AsyncSession=Depends(get_session),
    current_user:User=Depends(get_current_user)
):
    
    prod_stmt=select(Product).where(Product.id==payload.product_id)
    prod_res=await session.execute(prod_stmt)
    product=prod_res.scalar_one_or_none()
    
    if not product or product.inventory_count < payload.quantity:
        raise HTTPException(status_code=400, detail="Requested item stock allocation unavailable.")
    
    new_item=CartItem(user_id=current_user.id,product_id=payload.product_id,quantity=payload.quantity)
    await session.commit()
    await session.refresh(new_item)
    return new_item

