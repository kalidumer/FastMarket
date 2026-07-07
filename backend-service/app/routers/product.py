from fastapi import HTTPException,APIRouter,status,Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List,Optional
from sqlalchemy.orm import selectinload


from app.core.database import get_session
from app.models.product import (Product,ProductCreate,Category,ProductUpdate,CategoryBase)
from app.core.auth_guard import RoleChecker
from app.models.user import UserRole,User


STAFF_ROLE=RoleChecker([UserRole.ADMIN,UserRole.MANAGER])

router=APIRouter(prefix="/api/products",tags=["E-commerce Product Management"])


#==========================SEARCHING FUNCTIONALITY===================================

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_session
from app.models.product import Product # Ensure this points to your Product model

@router.get("/search", response_model=List[Product])
async def search_products(
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    session: AsyncSession = Depends(get_session)
):
    stmt = select(Product)
    

    if q:
        stmt = stmt.where(or_(
            Product.title.ilike(f"%{q}%"), 
            Product.description.ilike(f"%{q}%")
        ))
        
    if category_id:
        stmt = stmt.where(Product.category == category_id)
        
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
        
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)    
        
    stmt = stmt.order_by(Product.created_at.desc())
    
    search_result = await session.execute(stmt)
    
    return search_result.scalars().all()


#GET ALL PRODUCTS

@router.get("/",response_model=List[Product])
async def get_all_product(session:AsyncSession=Depends(get_session)):
    stmt=select(Product).order_by(Product.created_at.desc())
    result=await session.execute(stmt)
    products= result.scalars().all()

    if not result:
        raise HTTPException(status=404,detail="SEARCHING FOR ALL PRODUCT IS UNSUCCESSFUL,NO PRODUCT EXIST!")
    
    return products
    
#GET ONE PRODUCT

@router.get("/{product_id}",response_model=Product)
async def get_one_product(productId:int,
                          session:AsyncSession=Depends(get_session)):

    stmt=select(Product).where(Product.id==productId)
    result=await session.execute(stmt)
    product=result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status=404,detail="THERE IS NO PRODUCT WITH GIVEN ID")
    
    return product

#TO CREATE NEW PRODUCT

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_new_product(
    payload: ProductCreate,
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLE)
):
    # Check if the specified category exists
    stmt = select(Category).where(Category.id == payload.category)
    

    result = await session.execute(stmt)
    existed_category = result.scalar_one_or_none()
    
    if not existed_category:
        raise HTTPException(
            status_code=400, 
            detail="There is no wanted category to add the new product"
        )
    
    new_product = Product.model_validate(payload)
    session.add(new_product)
    
    await session.commit()
    await session.refresh(new_product)
    
    return new_product

# TO UPDATE THE PRODUCT INFORMATIONS

@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int, # Matches {product_id} in the path
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLE)
):
    # Fetch the existing data from the database first
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    db_product = result.scalar_one_or_none()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="THE PRODUCT WANTED TO BE UPDATED DOES NOT EXIST!"
        )
    
    # Extract only the fields sent in the request body (ignores missing fields)
    updated_data = payload.model_dump(exclude_unset=True)
    
    # Safety Check: If the admin is updating the category, verify the new category exists
    if "category" in updated_data and updated_data["category"] is not None:
        category_stmt = select(Category).where(Category.id == updated_data["category"])
        category_result = await session.execute(category_stmt)
        if not category_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category ID {updated_data['category']} does not exist."
            )
            
    # Loop and overwrite only the changed fields on top of the existing data
    for key, value in updated_data.items():
        setattr(db_product, key, value)
        
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)
    
    return db_product

#DELETE PRODUCT

@router.delete("/{productId}",response_model=Product)
async def delete_product(product_id:int,
                        session:AsyncSession=Depends(get_session),
                        current_staff:User=Depends(STAFF_ROLE)
                        ):
    stmt=select(Product).where(Product.id==product_id)
    result=await session.execute(stmt)
    product=result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404,detail="THE PRODUCT WANTED TO BE DELETED IS NOT EXIST!")
    
    session.delete(product)
    await session.commit()
    await session.refresh(product)
    return product

# ==================== CATEGORY MANAGEMENT ROUTES ====================

# @router.get("/categories", response_model=List[Category])
# async def list_all_categories(session: AsyncSession = Depends(get_session)):
#     stmt = select(Category).options(selectinload(Category.products)).order_by(Category.name)
#     result = await session.execute(stmt)
#     return result.unique().scalars().all()


@router.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryBase,
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLE)
):
    """Allows Admins or Managers to create new product categories."""
    # Prevent duplicate category names
    stmt = select(Category).where(Category.name == payload.name)
    existing = await session.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="A category with this name already exists.")
        
    new_category = Category.model_validate(payload)
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    return new_category

#==========================SEARCHING FUNCTIONALITY===================================

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_session
from app.models.product import Product # Ensure this points to your Product model

@router.get("/search", response_model=List[Product])
async def search_products(
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    session: AsyncSession = Depends(get_session)
):
    stmt = select(Product)
    

    if q:
        stmt = stmt.where(or_(
            Product.title.ilike(f"%{q}%"), 
            Product.description.ilike(f"%{q}%")
        ))
        
    if category_id:
        stmt = stmt.where(Product.category == category_id)
        
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
        
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)    
        
    stmt = stmt.order_by(Product.created_at.desc())
    
    search_result = await session.execute(stmt)
    
    return search_result.scalars().all()