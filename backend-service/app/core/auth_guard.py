import jwt
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_session
from app.models.user import User
from app.core.security import SECRET_KEY,ALGORITHM



# Order the fastapi TO Auto extract the Generated Token to bring out information and validation(decoding)

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
    except jwt.PyJWTError:
        raise credentials_exception
    
    
    statement = select(User).where(User.id == int(user_id))
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    
    
    class RoleChecker:
        #let's intialise the class with constructor and with a list of of str (role) 
        def __init__(self,allowed_roles:list[str]):
            self.allowed_roles=allowed_roles
       
        def __call__(self, current_user: User = Depends(get_current_user)):
            
            if current_user.role not in self.allowed_roles:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not have permissions for this action."
            )
             
            return current_user