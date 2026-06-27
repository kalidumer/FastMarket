from fastapi import HTTPException, status, Depends, APIRouter
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Data imported from files created before
from app.models.user import (
    UserResponse, UserRegister, User, UserRole, 
    TokenResponse, UserLogin, UserUpdate, RoleUpdate
)
from app.core.database import get_session
from app.core.security import hash_password, verify_passwords, create_access_token
from app.core.auth_guard import get_current_user, RoleChecker

router = APIRouter(prefix="/api", tags=["USER MANAGEMENT AND ROLES MANAGEMENT"])

# ==================== PUBLIC AUTH ENDPOINTS ====================

# ==============Register===================

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegister, session: AsyncSession = Depends(get_session)):
    # FIX: Removed await from select()
    stmt = select(User).where(User.email == payload.email)
    existing_user = await session.execute(stmt)
    
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="This User already Exist in this system")
    
    newUser = User(
        email=payload.email,
        full_name=payload.full_name,
        hash_password=hash_password(payload.password),
        role=UserRole.CUSTOMER
    )
    session.add(newUser)
    await session.commit()
    # FIX: Added newUser inside refresh()
    await session.refresh(newUser)
    return newUser

# =================Login=====================

@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: UserLogin, session: AsyncSession = Depends(get_session)):
    # FIX: Removed await from select()
    stmt = select(User).where(User.email == payload.email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    # FIX: Fixed function name to verify_passwords and separated args cleanly. Also fixed 'detail' key typo.
    if not user or not verify_passwords(payload.password, user.hash_password):
        raise HTTPException(status_code=401, detail="Email or password are Incorrect, Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="The user is not active now")
    
    token = create_access_token(user_id=user.id, role=user.role.value)
    
    return {
        "access_token": token,
        "token_type": "bearer", # FIX: Fixed typo "brearer"
        "role": user.role,
        "full_name": user.full_name
    }
    
# ===================== FOR ADMIN ONLY =====================================

# GET ALL USERS ONLY ADMIN OR MANAGER CAN DO THIS
    
@router.get("/admin/users", response_model=List[UserResponse])
async def read_all_user(
    session: AsyncSession = Depends(get_session),
    admin_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.MANAGER])) # FIX: Array in parentheses
):
   
    stmt = select(User).order_by(User.id)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/admin/user/{user_id}", response_model=UserResponse) # FIX: Changed path parameter to user_id
async def read_one_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    admin_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPPORT_AGENT]))
):
    # FIX: Removed await from select()
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="This user is not found in our system")
    
    return user

@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_users_profile(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    admin_user: User = Depends(RoleChecker([UserRole.ADMIN]))
):
    # FIX: Removed await from select()
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="The user wanted to update is not found!")
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user

@router.patch("/admin/users/{user_id}/role", response_model=UserResponse) # FIX: Added leading slash and user_id parameter
async def update_user_role(
    user_id: int,
    payload: RoleUpdate,
    session: AsyncSession = Depends(get_session),
    admin_user: User = Depends(RoleChecker([UserRole.ADMIN]))
):
    # FIX: Removed await from select()
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none() # FIX: Added missing parentheses ()
    
    if not user:
        raise HTTPException(status_code=404, detail="The user you are going to update the role is not found on the system!")
    
    user.role = payload.role
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user

@router.delete("/admin/users/{user_id}", status_code=status.HTTP_200_OK) # FIX: Checked naming to user_id
async def delete_user_permanently(
    user_id: int, # FIX: Added implicit typing
    session: AsyncSession = Depends(get_session),
    admin_user: User = Depends(RoleChecker([UserRole.ADMIN]))
):
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="YOU CANNOT KILL YOURSELF SINCE THIS ACCOUNT IS ADMIN!")
    
    # FIX: Removed await from select()
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User is not found to be deleted")
    
    await session.delete(user)
    await session.commit()
    # FIX: Removed session.refresh(user) as it breaks tracking post-deletion
    
    return {"status": "success", "message": f"The user #{user_id} is deleted permanently"}