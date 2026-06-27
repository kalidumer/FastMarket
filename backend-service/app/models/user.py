from enum import Enum
from typing import Optional, List
from pydantic import EmailStr, BaseModel
from sqlmodel import SQLModel, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    SUPPORT_AGENT = "support_agent"
    MANAGER = "manager"
    CUSTOMER = "customer"

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, nullable=False)
    full_name: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.CUSTOMER, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    
class User(UserBase,table=True):
    
    id:Optional[int]=Field(primary_key=True,nullable=False)
    hash_password:str=Field(nullable=False)
    
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    full_name: str
    
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True
        
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    
class RoleUpdate(BaseModel):
    role: UserRole