import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
from sqlmodel import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import Client, create_client

from app.core.database import get_session
from app.models.product import Product, Category, ProductUpdate
from app.core.auth_guard import RoleChecker
from app.models.user import UserRole, User

# Initialize Supabase Client
SUPABASE_URL = "https://your-supabase-project.supabase.co"
SUPABASE_KEY = "your-supabase-service-role-or-anon-key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_NAME = "ecommerce"

STAFF_ROLE = RoleChecker([UserRole.ADMIN, UserRole.MANAGER])

router = APIRouter(prefix="/api/products", tags=["E-commerce Product Management"])


# Helper function to upload image files to Supabase Storage
async def upload_file_to_supabase(file: UploadFile, folder: str) -> str:
    try:
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"

        contents = await file.read()

        supabase.storage.from_(BUCKET_NAME).upload(
            path=unique_filename,
            file=contents,
            file_options={"content-type": file.content_type or "image/jpeg"}
        )

        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(unique_filename)
        return public_url

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


# ========================== SEARCH & FETCH ROUTES ==========================

@router.get("/search", response_model=List[Product])
async def search_products(
    q: Optional[str] = None,
    category_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    session: AsyncSession = Depends(get_session)
):
    stmt = select(Product)

    if q:
        stmt = stmt.where(or_(
            Product.title.ilike(f"%{q}%"),
            Product.desc.ilike(f"%{q}%")
        ))

    if category_id:
        stmt = stmt.where(Product.category == category_id)

    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)

    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    stmt = stmt.order_by(Product.id.desc())

    search_result = await session.execute(stmt)
    return search_result.scalars().all()


@router.get("/", response_model=List[Product])
async def get_all_product(session: AsyncSession = Depends(get_session)):
    stmt = select(Product)
    result = await session.execute(stmt)
    products = result.scalars().all()

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SEARCHING FOR ALL PRODUCT IS UNSUCCESSFUL, NO PRODUCT EXIST!"
        )

    return products


@router.get("/{product_id}", response_model=Product)
async def get_one_product(
    product_id: str,
    session: AsyncSession = Depends(get_session)
):
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="THERE IS NO PRODUCT WITH GIVEN ID")

    return product


# ========================== PRODUCT CRUD WITH FILE UPLOADS ==========================

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_new_product(
    title: str = Form(...),
    desc: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    rating: float = Form(0.0),
    reviewCount: int = Form(0),
    isNew: bool = Form(True),
    images: List[UploadFile] = File(...),  # Accepts 1 to 3 images
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLE)
):
    # 1. Enforce max limit of 3 images
    if len(images) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 images allowed for a product."
        )

    # 2. Check if the specified category exists
    stmt = select(Category).where(Category.id == category)
    result = await session.execute(stmt)
    existed_category = result.scalar_one_or_none()

    if not existed_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is no wanted category to add the new product"
        )

    # 3. Upload images to Supabase Storage
    uploaded_urls = []
    for img in images:
        if not img.content_type or not img.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {img.filename} is not a valid image."
            )
        url = await upload_file_to_supabase(img, folder="products")
        uploaded_urls.append(url)

    # 4. Serialize images list to JSON string (or store as single URL / JSON list depending on your schema)
    # Storing array of URLs as JSON string to match frontend 'image: string' requirement
    image_str = json.dumps(uploaded_urls) if len(uploaded_urls) > 1 else uploaded_urls[0]

    # 5. Save product to Database
    new_product = Product(
        title=title,
        desc=desc,
        price=price,
        category=category,
        rating=rating,
        reviewCount=reviewCount,
        isNew=isNew,
        image=image_str
    )

    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)

    return new_product


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLE)
):
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="THE PRODUCT WANTED TO BE UPDATED DOES NOT EXIST!"
        )

    updated_data = payload.model_dump(exclude_unset=True)

    if "category" in updated_data and updated_data["category"] is not None:
        category_stmt = select(Category).where(Category.id == updated_data["category"])
        category_result = await session.execute(category_stmt)
        if not category_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category ID {updated_data['category']} does not exist."
            )

    for key, value in updated_data.items():
        setattr(db_product, key, value)

    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)

    return db_product


@router.delete("/{product_id}", response_model=Product)
async def delete_product(
    product_id: str,
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLE)
):
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="THE PRODUCT WANTED TO BE DELETED DOES NOT EXIST!"
        )

    await session.delete(product)
    await session.commit()
    return product


# ========================== CATEGORY MANAGEMENT ROUTES ==========================

@router.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    name: str = Form(...),
    itemCount: str = Form("0"),
    image: UploadFile = File(...),  # Max 1 file required for Category
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLE)
):
    # Prevent duplicate category names
    stmt = select(Category).where(Category.name == name)
    existing = await session.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A category with this name already exists."
        )

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a valid image."
        )

    # Upload single image to Supabase
    image_url = await upload_file_to_supabase(image, folder="categories")

    new_category = Category(
        name=name,
        image=image_url,
        itemCount=itemCount
    )

    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)

    return new_category