"""
Authentication Routes
Secure login/logout with JWT tokens
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from core.auth import (
    verify_password,
    create_access_token,
    get_current_user,
    USERS_DB
)

router = APIRouter(prefix="/auth", tags=["authentication"])

security = HTTPBasic()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Secure login endpoint
    Returns JWT token on successful authentication
    """
    # Find user
    user = USERS_DB.get(credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["username"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "email": user["email"]
        }
    }

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user info"""
    return {
        "username": current_user["username"],
        "email": current_user["email"]
    }

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout endpoint (client should delete token)"""
    return {"message": "Successfully logged out"}
