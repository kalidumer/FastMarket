from fastapi import HTTPException,status,Depends,APIRouter
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# we will import data from files created before
from app.models.user import (UserResponse,UserRegister,User,UserRole,TokenResponse,UserLogin,UserUpdate,RoleUpdate)
from app.core.database import get_session
from app.core.security import hash_password,verify_passwords,create_access_token
from app.core.auth_guard import RoleChecker

router=APIRouter(prefix="/api",tags=["USER MANAGEMENT AND ROLES MANAGEMENT"])

# TO CREATE A USER
@router.post("/auth/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)

async def register_user(payload:UserRegister,session:AsyncSession=Depends(get_session)):
    smt=await select(User).where(User.email == payload.email)
    existing_user=await session.execute(smt)
    
    if(existing_user.scalar_one_or_none()):
        raise HTTPException(status_code=400,detail="This User already Exist in this system")
    
    newUser= User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=UserRole.CUSTOMER
    )
    session.add(newUser)
    await session.commit()
    await session.refresh()
    return newUser

@router.post("/auth/login",response_model=TokenResponse)
async def Login(payload:UserLogin,session:AsyncSession=Depends(get_session)):
    
    stmt=await select(User).where(User.email == payload.email)
    result=await session.execute(stmt)
    user=result.scalar_one_or_none()
    
    if(not user or not verify_passwords(payload.password == user.hashed_password)):
        raise HTTPException(status_code=401 ,details="Email or password are Incorrect,Invalid creditials")
    
    if(not user.is_active):
        raise HTTPException(status_code=403,detail="the user is not active now")
    
    token=create_access_token(user_id=user.id,role=user.role.value)
    
    return{
        "access_token":token,
        "token_type":"brearer",
        "role":user.role,
        "full_name":user.full_name
    }
    
    #=================For ADMIN only================
    
@router.get("/admin/users",response_model=List[UserResponse])
async def read_all_user(session:AsyncSession=Depends(get_session),
                        admin_user:User=Depends(RoleChecker[UserRole.ADMIN,UserRole.MANAGER])):
    
    stmt=await select(User).order_by(User.id)
    result=await session.execute(stmt)
    return result.scalars().all()

@router.get("/admin/user/{userId}",response_model=UserResponse)
async def read_one_user(user_id:int,session:AsyncSession=Depends(get_session),
                        admin_user:User=Depends(RoleChecker[UserRole.ADMIN,UserRole.MANAGER,UserRole.SUPPORT_AGENT])):
    
    stmt=await select(User).where(User.id == user_id)
    result=await session.execute(stmt)
    user=result.scalar_one_or_none()
    
    if(not user):
        raise HTTPException(status_code=404,detail="This is user is not found in our system")
    
    return user

@router.put("admin/users/{userId}",response_model=UserResponse)
async def update_users_profile(user_id:int,payload:UserUpdate,session:AsyncSession=Depends(get_session),
                               admin_user:User=Depends(RoleChecker[UserRole.ADMIN])):
    stmt=await select(User).where(User.id== user_id)
    result=await session.execute(stmt)
    user=result.scalar_one_or_none()
    
    if (not user):
        raise HTTPException(status_code=404,detail="Th user wanted to update is not found!")
    
    update_data=payload.model_dump(exclude_unset=True)
    for key , value in update_data.items():
        setattr(user, key , value)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user

@router.patch("admin/users/{userId}/role",response_model=UserResponse)
async def update_user_role(
    user_id:int,
    payload:RoleUpdate,
    session:AsyncSession=Depends(get_session),
    admin_user:User=Depends(RoleChecker[UserRole.ADMIN])
):
    
    stmt=await select(User).where(User.id==user_id)
    result=await session.execute(stmt)
    user=result.scalar_one_or_none
    
    if not user:
        raise HTTPException(status_code=404,detail="the user you going to update the role is no fouund on the system!")
    
    user.role=payload.role
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user

@router.delete("/admin/users/{userId}",status_code=status.HTTP_200_OK)

async def delete_user_permanently(user_id,session:AsyncSession=Depends(get_session),admin_user:User=Depends(RoleChecker[UserRole.ADMIN])):
    
    if (user_id==admin_user.id):
        raise HTTPException(status_code=400,detail="YOU CANNOT KILL YOURSELF SINCE THIS ACCOUNT IS ADMIN!")
    
    stmt=await select(User).where(User.id == user_id)
    result=await session.execute(stmt)
    user=result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404,detail="user is not found to be deleted")
    
    session.delete(user)
    await session.commit()
    await session.refresh(user)
    
    return{"status":"success","message":f"the user #{userId} is deleted permanently"}
    
    