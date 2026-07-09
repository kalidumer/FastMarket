import uuid
import hmac
import hashlib
import os
import json
from fastapi import HTTPException, APIRouter, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from datetime import datetime

from app.models.order import (CartItem, CartBase, Order, OrderItem, OrderStatus, Payment, PaymentStatus)
from app.core.auth_guard import get_current_user
from app.core.database import get_session
from app.models.user import User
from app.models.product import Product
from app.services.payment import ChapaPaymentService as PaymentService

router = APIRouter(prefix="/api/order", tags=["Order Management Related"])

CHAPA_WEBHOOK_SECRET = os.getenv("CHAPA_WEBHOOK_SECRET", "your_webhook_secret_here")

# ==========================================
# 1. ADD / UPDATE CART QUANTITY
# ==========================================
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
    
    # Check if this item is already in the user's cart
    cart_stmt = select(CartItem).where(CartItem.user_id == current_user.id, CartItem.product_id == payload.product_id)
    cart_res = await session.execute(cart_stmt)
    existing_item = cart_res.scalar_one_or_none()
    
    if existing_item:
        # Update mode: overwrite previous values with updated quantities
        existing_item.quantity = payload.quantity
        session.add(existing_item)
        new_item = existing_item
    else:
        # Insertion mode
        new_item = CartItem(
            user_id=current_user.id,
            product_id=payload.product_id,
            quantity=payload.quantity
        )
        session.add(new_item)
    
    await session.commit()
    await session.refresh(new_item)
    return new_item


# ==========================================
# 2. CHECKOUT TRANSACTION LOGIC
# ==========================================
@router.post("/checkout", status_code=status.HTTP_201_CREATED)
async def checkout_cart(
    session: AsyncSession = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    # Fetch user's cart items
    cart_stmt = select(CartItem).where(CartItem.user_id == current_user.id)
    cart_res = await session.execute(cart_stmt)
    cart_items = cart_res.scalars().all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cannot checkout an empty shopping cart.")
        
    running_total = 0.0
    order_items_to_create = []
    
    # Verify stock and deduct inventory
    for item in cart_items:
        prod_stmt = select(Product).where(Product.id == item.product_id)
        prod_res = await session.execute(prod_stmt)
        product = prod_res.scalar_one_or_none()
        
        if not product or product.inventory_count < item.quantity:
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
        
    # Generate unique transaction reference string
    unique_tx_ref = f"fastmarket-{current_user.id}-{uuid.uuid4().hex[:6]}"
    
    # Create parent Order in PENDING state
    new_order = Order(
        user_id=current_user.id, 
        total_price=running_total, 
        status=OrderStatus.PENDING,
        txt_ref=unique_tx_ref[cite: 1]
    )
    session.add(new_order)
    await session.flush()  # Flushes record to generate new_order.id
    
    # Map out and link the child individual order items
    for order_item in order_items_to_create:
        order_item.order_id = new_order.id
        session.add(order_item)
        
    # Create the secondary Payment tracking entity (Initial state is PENDING)
    new_payment = Payment(
        order_id=new_order.id,
        txt_ref=unique_tx_ref,
        amount=running_total,
        status=PaymentStatus.PENDING
    )
    session.add(new_payment)
        
    # Request the Chapa Hosted Checkout Session Link
    try:
        payment_session = await PaymentService.initialize_chapa_payment(
            order_id=str(new_order.id),
            amount=running_total,
            currency="ETB",
            email=current_user.email,
            full_name=current_user.full_name if current_user.full_name else "Market Customer"
        )
    except Exception as e:
        # Clean transaction fallback strategy: rollback inventory holds if handshakes break down
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, 
            detail=f"Failed to communicate checkout initialization with Chapa gateway: {str(e)}"
        )
    
    # Clear active cart rows upon successful checkout execution
    for item in cart_items:
        await session.delete(item)
        
    await session.commit()
    
    return {
        "status": "awaiting_payment", 
        "order_id": new_order.id, 
        "checkout_url": payment_session["checkout_url"],
        "txt_ref": unique_tx_ref
    }


# ==========================================
# 3. SECURE VERIFICATION WEBHOOK
# ==========================================
@router.post("/payment/webhook")
async def chapa_payment_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    raw_body = await request.body()
    
    # Read security headers sent by Chapa to protect endpoint against attacks
    chapa_signature = request.headers.get("x-chapa-signature") or request.headers.get("Chapa-Signature")
    if not chapa_signature:
        raise HTTPException(status_code=401, detail="Missing mandatory checkout source signature header.")
        
    expected_signature = hmac.new(
        CHAPA_WEBHOOK_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, chapa_signature):
        raise HTTPException(status_code=401, detail="Webhook payload validation failed hash matches.")

    payload = json.loads(raw_body)
    tx_ref = payload.get("tx_ref")[cite: 1]
    status_event = payload.get("status")
    
    # Query order and payment rows matching tx_ref
    stmt = select(Order).where(Order.txt_ref == tx_ref)[cite: 1]
    res = await session.execute(stmt)
    order = res.scalar_one_or_none()
    
    pay_stmt = select(Payment).where(Payment.txt_ref == tx_ref)
    pay_res = await session.execute(pay_stmt)
    payment_record = pay_res.scalar_one_or_none()
    
    if not order or not payment_record:
        raise HTTPException(status_code=404, detail="Webhook payload transaction reference mapping not found.")
        
    # Idempotency guard: Avoid double processing if route was triggered previously
    if order.status == OrderStatus.PAID:
        return {"status": "already_processed"}
        
    # 3. Handle Payment Success
    if status_event == "success" or payload.get("event") == "charge.success":
        # Update main parent order status
        order.status = OrderStatus.PAID[cite: 1]
        
        # Update detailed audit trace entry lines
        payment_record.status = PaymentStatus.SUCCESSFUL
        payment_record.chapa_id = payload.get("reference")  # Stores Chapa's internal reference tracker
        payment_record.method = payload.get("payment_method")  # Captured payment channel type
        payment_record.updated_at = datetime.utcnow()
        
        session.add(order)
        session.add(payment_record)
        await session.commit()
        return {"status": "success", "message": "Order invoice successfully closed out."}[cite: 1]
        
    # 4. Handle Payment Failures / Cancellations
    else:
        order.status = OrderStatus.CANCELLED[cite: 1]
        
        payment_record.status = PaymentStatus.FAILED
        payment_record.updated_at = datetime.utcnow()
        
        session.add(order)
        session.add(payment_record)
        
        # Fetch related items to return held stock back to inventory
        items_stmt = select(OrderItem).where(OrderItem.order_id == order.id)[cite: 1]
        items_res = await session.execute(items_stmt)
        ordered_items = items_res.scalars().all()[cite: 1]
        
        if ordered_items:
            product_ids = [item.product_id for item in ordered_items]
            prod_stmt = select(Product).where(Product.id.in_(product_ids))
            prod_res = await session.execute(prod_stmt)
            products_map = {p.id: p for p in prod_res.scalars().all()}
            
            for item in ordered_items:
                product = products_map.get(item.product_id)
                if product:
                    product.inventory_count += item.quantity  # Return held stock back to shelves[cite: 1]
                    session.add(product)
                
        await session.commit()
        return {"status": "failed", "message": "Transaction failed. Stock inventory holdings returned."}[cite: 1]


# ==========================================
# 4. DYNAMIC AI RECOMMENDATIONS
# ==========================================
@router.get("/ai-recommendations", response_model=List[Product])
async def dynamic_ai_upsell(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    last_order_stmt = select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())[cite: 1]
    last_order_res = await session.execute(last_order_stmt)[cite: 1]
    last_order = last_order_res.scalar_one_or_none()[cite: 1]
    
    if not last_order:
        fallback_stmt = select(Product).order_by(Product.inventory_count.desc()).limit(3)[cite: 1]
        fallback_res = await session.execute(fallback_stmt)[cite: 1]
        return fallback_res.scalars().all()[cite: 1]
        
    items_stmt = select(OrderItem).where(OrderItem.order_id == last_order.id)[cite: 1]
    items_res = await session.execute(items_stmt)[cite: 1]
    purchased_item = items_res.scalars().first()[cite: 1]
    
    if purchased_item:
        ref_prod_stmt = select(Product).where(Product.id == purchased_item.product_id)[cite: 1]
        ref_prod_res = await session.execute(ref_prod_stmt)[cite: 1]
        ref_product = ref_prod_res.scalar_one_or_none()[cite: 1]
        
        if ref_product:
            recommend_stmt = select(Product).where(
                Product.category_id == ref_product.category_id,
                Product.id != ref_product.id,
                Product.inventory_count > 0
            ).limit(3)[cite: 1]
            rec_res = await session.execute(recommend_stmt)[cite: 1]
            return rec_res.scalars().all()[cite: 1]
            
    final_stmt = select(Product).limit(3)[cite: 1]
    final_res = await session.execute(final_stmt)[cite: 1]
    return final_res.scalars().all()[cite: 1]