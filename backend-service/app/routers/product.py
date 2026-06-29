from fastapi import HTTPException,APIRouter,status,Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List,Optional


from app.core.database import get_session
from app.models.product import (Product,ProductCreate,Category,ProductUpdate,CategoryBase)
from app.core.auth_guard import RoleChecker
from app.models.user import UserRole,User


STAFF_ROLE=RoleChecker([UserRole.ADMIN,UserRole.MANAGER])

router=APIRouter(prefix="/api/catelog",tags=["E-commerce catelog engine"])

#GET ALL PRODUCTS

@router.get("/products",response_model=List[Product])
async def get_all_product(session:AsyncSession=Depends(get_session)):
    stmt=select(Product).order_by(Product.created_at.desc())
    result=await session.execute(stmt)
    products= result.scalars().all()

    if not result:
        raise HTTPException(status=404,detail="SEARCHING FOR ALL PRODUCT IS UNSUCCESSFUL,NO PRODUCT EXIST!")
    
    return products
    
#GET ONE PRODUCT

@router.get("/products/{product_id}",response_model=Product)
async def get_one_product(productId:int,
                          session:AsyncSession=Depends(get_session)):

    stmt=select(Product).where(Product.id==productId)
    result=await session.execute(stmt)
    product=result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status=404,detail="THERE IS NO PRODUCT WITH GIVEN ID")
    
    return product

#TO CREATE NEW PRODUCT

@router.post("/products",response_model=Product,status_code=status.HTTP_201_CREATED)
async def create_new_product(payload:ProductCreate,
                         session:AsyncSession=Depends(get_session),
                         current_staff:User=Depends(STAFF_ROLE)):
    
#check if already created on some category first
    
    stmt=select(Category).where(Category.id==payload.category_id)
    existedCategory=await session.excute(stmt)
    
    if not existedCategory.scalar_one_or_none():
        raise HTTPException(status=400,detail="There is no wanted category to add the new product")
    
    new_product=Product.model_validate(payload)
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    return new_product

# TO UPDATE THE PRODUCT INFORMATIONS

@router.put("/products/{productId}",response_model=Product)
async def update_product(product_id:int,
                        payload:ProductUpdate,
                        session:AsyncSession=Depends(get_session),
                        current_staff:User=Depends(STAFF_ROLE)
                        ):
    
    stmt=select(Product).where(Product.id==product_id)
    result=await session.execute(stmt)
    products=result.scalar_one_or_none()
    if not products:
        raise HTTPException(status_code=404,detail="THE PRODUCT WANTED TO BE UPDATED IS NOT EXIST!")
    
    updated_data=payload.model_dump(exclude_unset=True)
    
    for key,value in updated_data.items():
        setattr(products,key,value)
        
    session.add(products)
    await session.commit()
    await session.refresh(products)
    return products

#DELETE PRODUCT

@router.put("/products/{productId}",response_model=Product)
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

@router.get("/categories", response_model=List[Category])
async def list_all_categories(session: AsyncSession = Depends(get_session)):
    """Public endpoint to fetch all product categories for navigation menus."""
    stmt = select(Category).order_by(Category.name)
    result = await session.execute(stmt)
    return result.scalars().all()


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

@router.get("/search", response_model=List[Product])
async def search_products(
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    session: AsyncSession = Depends(get_session)
):
    stmt=select(Product)
    if q:
        stmt=stmt.where(Product.title.ilike(f"%{q}%") | Product.description.ilike(f"%{q}%"))
        
    if category_id:
        stmt=stmt.where(Product.category_id==category_id)
        
    if min_price is not None:
        stmt=stmt.where(Product.price >= min_price)
        
    if max_price is not None:
        stmt=stmt.where(Product.price <= max_price)    
        
    stmt=stmt.order_by(Product.created_at.desc())
    
    search_result= await session.excute(stmt)
    
    return search_result.scalars().all()