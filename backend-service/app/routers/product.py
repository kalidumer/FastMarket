from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_session
from app.models.product import Product, ProductCreate, ProductUpdate, Category
from app.core.auth_guard import RoleChecker
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/catalog", tags=["E-commerce Catalog Engine"])

# 🔒 Guards: Staff privileges required to mutate inventory items
STAFF_ROLES = RoleChecker([UserRole.ADMIN, UserRole.MANAGER])

# ==================== PUBLIC ROUTES (For Customers & Guests) ====================

@router.get("/products", response_model=List[Product])
async def list_all_products(session: AsyncSession = Depends(get_session)):
    """Fetch all available items in the e-commerce store."""
    stmt = select(Product).order_by(Product.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/products/{product_id}", response_model=Product)
async def get_single_product(product_id: int, session: AsyncSession = Depends(get_session)):
    """Fetch details of a single product entry."""
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product

# ==================== PROTECTED MANAGEMENT ROUTES ====================

@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_new_product(
    payload: ProductCreate, 
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLES)
):
    """Allows Admins or Managers to create store products."""
    # Verify that the designated category exists first
    category_stmt = select(Category).where(Category.id == payload.category_id)
    category_check = await session.execute(category_stmt)
    if not category_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="The assigned Category ID does not exist.")

    new_product = Product.model_validate(payload)
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    return new_product

@router.put("/products/{product_id}", response_model=Product)
async def modify_product(
    product_id: int,
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLES)
):
    """Allows modification of inventory descriptions, pricing, or metadata counters."""
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Target product database record not found.")
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
        
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product