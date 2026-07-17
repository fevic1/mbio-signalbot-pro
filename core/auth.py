"""
Secure Authentication Module
Implements bcrypt password hashing and JWT token management
"""
import os
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Security schemes
security = HTTPBearer()

# User model
class User(BaseModel):
    username: str
    email: str
    hashed_password: str

# Mock user database (replace with real database in production)
# Load admin credentials from environment variables
_admin_email = os.environ.get("MBIO_ADMIN_EMAIL", "admin@mbio.com")
_admin_password = os.environ.get("MBIO_ADMIN_PASSWORD")

if not _admin_password:
    raise ValueError("MBIO_ADMIN_PASSWORD environment variable is required")

USERS_DB = {
    _admin_email: {
        "username": _admin_email,
        "email": _admin_email,
        "hashed_password": "$2b$12$LQv3c1yqBo9SkvXS8QTpOeCQZqKqGqGqGqGqGqGqGqGqGqGqGqGqG"
    }
}

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if username is None or username not in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return USERS_DB[username]

# Initialize default user with proper password hash
def init_auth():
    """Initialize authentication with default user"""
    admin_email = os.environ.get("MBIO_ADMIN_EMAIL", "admin@mbio.com")
    admin_password = os.environ.get("MBIO_ADMIN_PASSWORD")
    if admin_password:
        USERS_DB[admin_email]["hashed_password"] = hash_password(admin_password)
        print(f"✅ Auth initialized for: {admin_email}")
    else:
        print("⚠️  MBIO_ADMIN_PASSWORD not set - auth not initialized")

init_auth()
