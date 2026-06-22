import os
from datetime import datetime,timedelta,timezone
from typing import Any,Union
import jwt
from passlib.context import CryptContext


SECRET_KEY=os.getenv("SECRET_KEY","super complext secret key")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTE=15

#INTIALIZING HASHING

psw_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(password:str)->str:
    return psw_context.hash(password)

def verify_passwords(plain_password:str,hash_password:str)->str:
    return psw_context.verify(plain_password,hash_password)

def create_access_token(subject:Union[str,any],role:str,expire_delta:timedelta=None)->str:
    
    if (expire_delta):
        expire=datetime.now(timezone.utc) + expire_delta
        
    else:
        expire=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE)
        
    to_encode={
        "exp":expire,
        "sub":str(subject),
        "role":role    
    }
    
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt