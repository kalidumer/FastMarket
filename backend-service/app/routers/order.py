from fastapi import HTTPException,APIRouter,status,Depends,Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List

from  app.models.order import (CartItem,CartBase,Order,OrderItem,OrderStatus)
from app.core.auth_guard import get_current_user
from app.core.database import get_session
from app.models.user import User
from app.models.product import Product
from app.services.payment import ChapaPaymentService as PaymentService



router=APIRouter(prefix="/api/order",tags=["Order Management Related"])

@router.post("/cart", response_model=CartItem)
async def add_to_cart(
    payload: CartBase,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    prod_stmt = select(Product).where(Product.id == payload.product_id)
    prod_res = await session.execute(prod_stmt)
    product = prod_res.scalar_one_or_none()
    
    if not product or product.inventory_count < payload.quantity:
        raise HTTPException(status_code=400, detail="Requested item stock allocation unavailable.")
    
    new_item = CartItem(
        user_id=current_user.id,
        product_id=payload.product_id,
        quantity=payload.quantity
    )
    
    session.add(new_item)
    
    await session.commit()
    await session.refresh(new_item)
    
    return new_item

#checkout endpoint to create a PENDING order and request a Chapa payment session

@router.post("/checkout", status_code=status.HTTP_201_CREATED)
async def checkout_cart(
    session: AsyncSession = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    """
    Executes transaction checkout logic. Holds inventory, compiles cart details,
    creates a PENDING order entity, and requests a secure Chapa payment session token.
    """
    # 1. Fetch live cart content
    cart_stmt = select(CartItem).where(CartItem.user_id == current_user.id)
    cart_res = await session.execute(cart_stmt)
    cart_items = cart_res.scalars().all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cannot checkout an empty shopping cart.")
        
    running_total = 0.0
    order_items_to_create = []
    
    # 2. Concurrency checks & Stock Allocation Lock
    for item in cart_items:
        prod_stmt = select(Product).where(Product.id == item.product_id)
        prod_res = await session.execute(prod_stmt)
        product = prod_res.scalar_one_or_none()
        
        if not product or product.inventory_count < item.quantity:
            await session.rollback()
            raise HTTPException(
                status_code=400, 
                detail=f"Stock unavailable for item: {product.title if product else 'Unknown'}."
            )
            
        # Deduct physical stock so nobody else buys it while this user pays
        product.inventory_count -= item.quantity
        session.add(product)
        
        running_total += (product.price * item.quantity)
        order_items_to_create.append(
            OrderItem(product_id=product.id, quantity=item.quantity, price_at_purchase=product.price)
        )
        
    # 3. Create the Parent Order entity in a PENDING state
    new_order = Order(user_id=current_user.id, total_price=running_total, status=OrderStatus.PENDING)
    session.add(new_order)
    await session.flush() # Flushes record to get access to new_order.id
    
    for order_item in order_items_to_create:
        order_item.order_id = new_order.id
        session.add(order_item)
        
    # 4. Request the Chapa Hosted Checkout Session Link
    payment_session = await PaymentService.initialize_chapa_payment(
        order_id=new_order.id,
        amount=running_total,
        email=current_user.email,
        full_name=current_user.full_name
    )
    
    # Update order with its transaction reference tracking tag
    new_order.tx_ref = payment_session["tx_ref"]
    session.add(new_order)
    
    # Clear active cart rows
    for item in cart_items:
        await session.delete(item)
        
    await session.commit()
    
    # Return response payload so frontend can perform window redirection to Telebirr / Card payment options
    return {
        "status": "awaiting_payment", 
        "order_id": new_order.id, 
        "checkout_url": payment_session["checkout_url"],
        "tx_ref": payment_session["tx_ref"]
    }
    
# Webhook endpoint to handle Chapa payment resolution callbacks

@router.post("/payment/webhook")
async def chapa_payment_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Asynchronous Webhook Endpoint hit by Chapa servers upon transaction resolution.
    Updates local orders to PAID or rolls back inventory constraints on failure.
    """
    # 1. Parse body stream from Chapa
    payload = await request.json()
    tx_ref = payload.get("tx_ref")
    event = payload.get("event") # Chapa generally sends a success status indicator
    
    # 2. Look up the corresponding order using our unique indexed reference tag
    stmt = select(Order).where(Order.tx_ref == tx_ref)
    res = await session.execute(stmt)
    order = res.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Webhook payload transaction reference mapping not found.")
        
    # Check if the order was already marked processed to avoid duplicate mutations
    if order.status == OrderStatus.PAID:
        return {"status": "already_processed"}
        
    # 3. Process payment success status update
    if payload.get("status") == "success" or event == "charge.success":
        order.status = OrderStatus.PAID
        session.add(order)
        await session.commit()
        return {"status": "success", "message": "Order invoice successfully closed out."}
        
    # 4. Process failure/cancellation states gracefully
    else:
        order.status = OrderStatus.CANCELLED
        session.add(order)
        
        # 🔄 CRITICAL ERROR HANDLING: Return held stock back to inventory if checkout fails
        items_stmt = select(OrderItem).where(OrderItem.order_id == order.id)
        items_res = await session.execute(items_stmt)
        ordered_items = items_res.scalars().all()
        
        for item in ordered_items:
            prod_stmt = select(Product).where(Product.id == item.product_id)
            prod_res = await session.execute(prod_stmt)
            product = prod_res.scalar_one_or_none()
            if product:
                product.inventory_count += item.quantity # Put the stock back on shelves
                session.add(product)
                
        await session.commit()
        return {"status": "failed", "message": "Transaction failed. Stock inventory holdings returned."}
    
# ==================== DATA-DRIVEN AI RECOMMENDATIONS ====================

@router.get("/ai-recommendations", response_model=List[Product])
async def dynamic_ai_upsell(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    E-Commerce Personalization Engine. Analyzes recent order history data
    structures to recommend contextual items from related categories.
    """
    # Fetch user's latest order to analyze their interests
    last_order_stmt = select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())
    last_order_res = await session.execute(last_order_stmt)
    last_order = last_order_res.scalar_one_or_none()
    
    if not last_order:
        # Fallback to general high-inventory products if user history is clean
        fallback_stmt = select(Product).order_by(Product.inventory_count.desc()).limit(3)
        fallback_res = await session.execute(fallback_stmt)
        return fallback_res.scalars().all()
        
    # Analyze the categories of items purchased in that order
    items_stmt = select(OrderItem).where(OrderItem.order_id == last_order.id)
    items_res = await session.execute(items_stmt)
    purchased_item = items_res.scalars().first()
    
    if purchased_item:
        ref_prod_stmt = select(Product).where(Product.id == purchased_item.product_id)
        ref_prod_res = await session.execute(ref_prod_stmt)
        ref_product = ref_prod_res.scalar_one_or_none()
        
        if ref_product:
            # Upsell strategy: Find other in-stock products within the same matching catalog tier
            recommend_stmt = select(Product).where(
                Product.category_id == ref_product.category_id,
                Product.id != ref_product.id,
                Product.inventory_count > 0
            ).limit(3)
            rec_res = await session.execute(recommend_stmt)
            return rec_res.scalars().all()
            
    # Universal fallback baseline match configuration if records yield empty metrics
    final_stmt = select(Product).limit(3)
    final_res = await session.execute(final_stmt)
    return final_res.scalars().all()