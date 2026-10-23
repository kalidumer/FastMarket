import uuid
import json
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
from sqlmodel import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import Client, create_client

from app.core.database import get_session
from app.models.product import Product, Category, ProductUpdate
from app.core.auth_guard import RoleChecker
from app.models.user import UserRole, User

# ========================== CONFIG & INITIALIZATION ==========================

SUPABASE_URL = "https://your-supabase-project.supabase.co"
SUPABASE_KEY = "your-supabase-service-role-or-anon-key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_NAME = "ecommerce"

STAFF_ROLE = RoleChecker([UserRole.ADMIN, UserRole.MANAGER])

router = APIRouter(prefix="/api/products", tags=["E-commerce Product Management"])


# ========================== SUPABASE HELPER FUNCTIONS ==========================

async def upload_file_to_supabase(file: UploadFile, folder: str) -> str:
    """Uploads a single file to Supabase Storage asynchronously in a thread executor."""
    try:
        file_extension = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
        unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"

        contents = await file.read()

        def _upload():
            supabase.storage.from_(BUCKET_NAME).upload(
                path=unique_filename,
                file=contents,
                file_options={"content-type": file.content_type or "image/jpeg"}
            )
            return supabase.storage.from_(BUCKET_NAME).get_public_url(unique_filename)

        public_url = await asyncio.to_thread(_upload)
        return public_url

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


def extract_storage_path_from_url(public_url: str) -> Optional[str]:
    """Extracts relative file path inside the bucket from public Supabase URL."""
    try:
        marker = f"/object/public/{BUCKET_NAME}/"
        if marker in public_url:
            return public_url.split(marker)[1]
    except Exception:
        pass
    return None


async def delete_files_from_supabase(image_urls: List[str]) -> None:
    """Removes one or multiple images from Supabase Storage asynchronously."""
    paths_to_delete = []
    
    for url in image_urls:
        path = extract_storage_path_from_url(url)
        if path:
            paths_to_delete.append(path)

    if not paths_to_delete:
        return

    try:
        def _delete():
            supabase.storage.from_(BUCKET_NAME).remove(paths_to_delete)

        await asyncio.to_thread(_delete)
    except Exception as e:
        print(f"Warning: Failed to delete image from storage: {str(e)}")


# ========================== CATEGORY MANAGEMENT ROUTES ==========================
# (MUST BE PLACED BEFORE PARSED DYNAMIC ID ROUTES LIKE /{product_id})

@router.get("/categories", response_model=List[Category])
async def get_all_categories(session: AsyncSession = Depends(get_session)):
    """Fetch all product categories sorted by name."""
    stmt = select(Category).order_by(Category.name.asc())
    result = await session.execute(stmt)
    categories = result.scalars().all()
    return categories


@router.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    name: str = Form(...),
    itemCount: str = Form("0"),
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLE)
):
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


@router.get("/categories/{category_id}", response_model=Category)
async def get_one_category(
    category_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Fetch a single category by its ID."""
    stmt = select(Category).where(Category.id == category_id)
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    return category


@router.delete("/categories/{category_id}", response_model=Category)
async def delete_category(
    category_id: str,
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLE)
):
    stmt = select(Category).where(Category.id == category_id)
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    product_stmt = select(Product).where(Product.category == category_id)
    product_check = await session.execute(product_stmt)
    if product_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category containing active products. Reassign or delete products first."
        )

    if category.image:
        await delete_files_from_supabase([category.image])

    await session.delete(category)
    await session.commit()
    return category


# ========================== SEARCH & LIST ROUTES ==========================

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


# ========================== DYNAMIC PRODUCT PARAMETER ROUTES ==========================
# (MUST STAY AT THE VERY BOTTOM OF THE ROUTER FILE)

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


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_new_product(
    title: str = Form(...),
    desc: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    rating: float = Form(0.0),
    reviewCount: int = Form(0),
    isNew: bool = Form(True),
    images: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_session),
    current_staff: User = Depends(STAFF_ROLE)
):
    if not images or len(images) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one image is required."
        )

    if len(images) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 images allowed for a product."
        )

    stmt = select(Category).where(Category.id == category)
    result = await session.execute(stmt)
    existed_category = result.scalar_one_or_none()

    if not existed_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is no wanted category to add the new product"
        )

    uploaded_urls = []
    for img in images:
        if not img.content_type or not img.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {img.filename} is not a valid image."
            )
        url = await upload_file_to_supabase(img, folder="products")
        uploaded_urls.append(url)

    image_str = json.dumps(uploaded_urls) if len(uploaded_urls) > 1 else uploaded_urls[0]

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

    urls_to_delete: List[str] = []
    if product.image:
        try:
            if product.image.startswith("["):
                urls_to_delete = json.loads(product.image)
            else:
                urls_to_delete = [product.image]
        except Exception:
            urls_to_delete = [product.image]

    if urls_to_delete:
        await delete_files_from_supabase(urls_to_delete)

    await session.delete(product)
    await session.commit()
    return product