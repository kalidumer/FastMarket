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
from pydantic import BaseModel, Field

from app.models.order import (CartItem, CartBase, Order, OrderItem, OrderStatus, Payment, PaymentStatus)
from app.core.auth_guard import get_current_user
from app.core.database import get_session
from app.models.user import User
from app.models.product import Product
from app.services.payment import ChapaPaymentService as PaymentService

router = APIRouter(prefix="/api/order", tags=["Order Management Related"])

CHAPA_WEBHOOK_SECRET = os.getenv("CHAPA_WEBHOOK_SECRET", "your_webhook_secret_here")

# Schema enforcing that selected item IDs must accompany the checkout request
class CheckoutRequest(BaseModel):
    cart_item_ids: List[int] = Field(..., min_items=1, description="List of specific CartItem IDs to checkout")

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
    
    cart_stmt = select(CartItem).where(CartItem.user_id == current_user.id, CartItem.product_id == payload.product_id)
    cart_res = await session.execute(cart_stmt)
    existing_item = cart_res.scalar_one_or_none()
    
    if existing_item:
        existing_item.quantity = payload.quantity
        session.add(existing_item)
        new_item = existing_item
    else:
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
# 2. CHECKOUT SELECTED ITEMS ONLY
# ==========================================
@router.post("/checkout", status_code=status.HTTP_201_CREATED)
async def checkout_cart(
    payload: CheckoutRequest,
    session: AsyncSession = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    # Fetch ONLY the selected items from the user's cart
    cart_stmt = select(CartItem).where(
        CartItem.user_id == current_user.id,
        CartItem.id.in_(payload.cart_item_ids)
    )
    cart_res = await session.execute(cart_stmt)
    cart_items = cart_res.scalars().all()
    
    if len(cart_items) != len(payload.cart_item_ids):
        raise HTTPException(
            status_code=400, 
            detail="One or more selected cart items could not be found or do not belong to you."
        )
        
    running_total = 0.0
    order_items_to_create = []
    
    for item in cart_items:
        prod_stmt = select(Product).where(Product.id == item.product_id)
        prod_res = await session.execute(prod_stmt)
        product = prod_res.scalar_one_or_none()
        
        if not product or product.inventory_count < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock unavailable for item: {product.title if product else 'Unknown'}."
            )
            
        product.inventory_count -= item.quantity
        session.add(product)
        
        running_total += (product.price * item.quantity)
        order_items_to_create.append(
            OrderItem(product_id=product.id, quantity=item.quantity, price_at_purchase=product.price)
        )
        
    unique_tx_ref = f"fastmarket-{current_user.id}-{uuid.uuid4().hex[:6]}"
    
    new_order = Order(
        user_id=current_user.id, 
        total_price=running_total, 
        status=OrderStatus.PENDING,
        txt_ref=unique_tx_ref
    )
    session.add(new_order)
    await session.flush()  
    
    for order_item in order_items_to_create:
        order_item.order_id = new_order.id
        session.add(order_item)
        
    new_payment = Payment(
        order_id=new_order.id,
        txt_ref=unique_tx_ref,
        amount=running_total,
        status=PaymentStatus.PENDING
    )
    session.add(new_payment)
        
    try:
        payment_session = await PaymentService.initialize_chapa_payment(
            order_id=str(new_order.id),
            amount=running_total,
            currency="ETB",
            email=current_user.email,
            full_name=current_user.full_name if current_user.full_name else "Market Customer",
            tx_ref=unique_tx_ref  
        )
        
        if not payment_session or "checkout_url" not in payment_session:
            raise ValueError("Chapa initialization response returned empty or malformed parameters.")

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, 
            detail=f"Failed to communicate checkout initialization with Chapa gateway: {str(e)}"
        )
    
    # Remove ONLY the checked-out items from the active cart rows
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
    tx_ref = payload.get("tx_ref")
    status_event = payload.get("status")
    
    stmt = select(Order).where(Order.txt_ref == tx_ref)
    res = await session.execute(stmt)
    order = res.scalar_one_or_none()
    
    pay_stmt = select(Payment).where(Payment.txt_ref == tx_ref)
    pay_res = await session.execute(pay_stmt)
    payment_record = pay_res.scalar_one_or_none()
    
    if not order or not payment_record:
        raise HTTPException(status_code=404, detail="Webhook payload transaction reference mapping not found.")
        
    if order.status == OrderStatus.PAID:
        return {"status": "already_processed"}
        
    if status_event == "success" or payload.get("event") == "charge.success":
        order.status = OrderStatus.PAID
        
        payment_record.status = PaymentStatus.SUCCESSFUL
        payment_record.chapa_id = payload.get("reference")  
        payment_record.method = payload.get("payment_method")  
        payment_record.updated_at = datetime.utcnow()
        
        session.add(order)
        session.add(payment_record)
        await session.commit()
        return {"status": "success", "message": "Order invoice successfully closed out."}
        
    else:
        order.status = OrderStatus.CANCELLED
        
        payment_record.status = PaymentStatus.FAILED
        payment_record.updated_at = datetime.utcnow()
        
        session.add(order)
        session.add(payment_record)
        
        items_stmt = select(OrderItem).where(OrderItem.order_id == order.id)
        items_res = await session.execute(items_stmt)
        ordered_items = items_res.scalars().all()
        
        if ordered_items:
            product_ids = [item.product_id for item in ordered_items]
            prod_stmt = select(Product).where(Product.id.in_(product_ids))
            prod_res = await session.execute(prod_stmt)
            products_map = {p.id: p for p in prod_res.scalars().all()}
            
            for item in ordered_items:
                product = products_map.get(item.product_id)
                if product:
                    product.inventory_count += item.quantity  
                    session.add(product)
                
        await session.commit()
        return {"status": "failed", "message": "Transaction failed. Stock inventory holdings returned."}


# ==========================================
# 4. MANUAL CHECKOUT STATUS VERIFICATION
# ==========================================
@router.get("/verify/{tx_ref}")
async def verify_checkout_payment(
    tx_ref: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Order).where(Order.txt_ref == tx_ref, Order.user_id == current_user.id)
    res = await session.execute(stmt)
    order = res.scalar_one_or_none()

    pay_stmt = select(Payment).where(Payment.txt_ref == tx_ref)
    pay_res = await session.execute(pay_stmt)
    payment_record = pay_res.scalar_one_or_none()

    if not order or not payment_record:
        raise HTTPException(status_code=404, detail="Transaction reference not found.")

    if order.status == OrderStatus.PAID:
        return {"status": "paid", "message": "Order has already been processed and marked as PAID."}

    try:
        verification_data = await PaymentService.verify_chapa_payment(tx_ref)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error communicating with Chapa verification endpoint: {str(e)}"
        )

    chapa_status = verification_data.get("data", {}).get("status")

    if verification_data.get("status") == "success" and chapa_status == "success":
        order.status = OrderStatus.PAID
        
        payment_record.status = PaymentStatus.SUCCESSFUL
        payment_record.chapa_id = verification_data["data"].get("reference")
        payment_record.method = verification_data["data"].get("payment_method")
        payment_record.updated_at = datetime.utcnow()

        session.add(order)
        session.add(payment_record)
        await session.commit()

        return {
            "status": "paid",
            "message": "Payment verified successfully! Order closed.",
            "amount": verification_data["data"].get("amount")
        }

    elif chapa_status == "failed":
        order.status = OrderStatus.CANCELLED
        payment_record.status = PaymentStatus.FAILED
        payment_record.updated_at = datetime.utcnow()

        session.add(order)
        session.add(payment_record)

        items_stmt = select(OrderItem).where(OrderItem.order_id == order.id)
        items_res = await session.execute(items_stmt)
        ordered_items = items_res.scalars().all()

        if ordered_items:
            product_ids = [item.product_id for item in ordered_items]
            prod_stmt = select(Product).where(Product.id.in_(product_ids))
            prod_res = await session.execute(prod_stmt)
            products_map = {p.id: p for p in prod_res.scalars().all()}

            for item in ordered_items:
                product = products_map.get(item.product_id)
                if product:
                    product.inventory_count += item.quantity
                    session.add(product)

        await session.commit()
        return {"status": "failed", "message": "Payment was declared failed by Chapa. Stock returned."}

    else:
        return {"status": "pending", "message": "Payment is still awaiting completion."}


# ==========================================
# 5. DYNAMIC AI RECOMMENDATIONS
# ==========================================
@router.get("/ai-recommendations", response_model=List[Product])
async def dynamic_ai_upsell(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    last_order_stmt = select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())
    last_order_res = await session.execute(last_order_stmt)
    last_order = last_order_res.scalar_one_or_none()
    
    if not last_order:
        fallback_stmt = select(Product).order_by(Product.inventory_count.desc()).limit(3)
        fallback_res = await session.execute(fallback_stmt)
        return fallback_res.scalars().all()
        
    items_stmt = select(OrderItem).where(OrderItem.order_id == last_order.id)
    items_res = await session.execute(items_stmt)
    purchased_item = items_res.scalars().first()
    
    if purchased_item:
        ref_prod_stmt = select(Product).where(Product.id == purchased_item.product_id)
        ref_prod_res = await session.execute(ref_prod_stmt)
        ref_product = ref_prod_res.scalar_one_or_none()
        
        if ref_product:
            recommend_stmt = select(Product).where(
                Product.category_id == ref_product.category_id,
                Product.id != ref_product.id,
                Product.inventory_count > 0
            ).limit(3)
            rec_res = await session.execute(recommend_stmt)
            return rec_res.scalars().all()
            
    final_stmt = select(Product).limit(3)
    final_res = await session.execute(final_stmt)
    return final_res.scalars().all()