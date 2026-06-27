import os
from datetime import datetime, timedelta, timezone
from typing import Any, Union
import jwt 
import bcrypt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "LOCAL_DEV_SECRET_KEY_CHANGE_IN_PRODUCTION_987654321")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hashes a plain text password using native bcrypt."""
    # Convert string to bytes, generate a salt, and hash it
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8') # Return as a clean string to store in DB

def verify_passwords(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against its stored bcrypt hash."""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(user_id: int, role: str, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(user_id),
        "role": role
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)