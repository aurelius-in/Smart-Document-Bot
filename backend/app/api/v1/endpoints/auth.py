from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import jwt
from passlib.context import CryptContext

from ...core.config import settings
from ...core.security import create_access_token, verify_token

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserInfo(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    permissions: list[str]
    is_active: bool
    created_at: str
    last_login: Optional[str] = None


# Mock user database - in production, this would be a real database
MOCK_USERS = {
    "admin@redline.com": {
        "id": "user_001",
        "email": "admin@redline.com",
        "username": "admin",
        "full_name": "System Administrator",
        "password_hash": pwd_context.hash("admin123"),
        "role": "admin",
        "permissions": ["read", "write", "delete", "analyze", "admin"],
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": None
    },
    "user@redline.com": {
        "id": "user_002",
        "email": "user@redline.com",
        "username": "user",
        "full_name": "Regular User",
        "password_hash": pwd_context.hash("user123"),
        "role": "user",
        "permissions": ["read", "write", "analyze"],
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": None
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(email: str):
    """Get user by email from mock database"""
    return MOCK_USERS.get(email)


def authenticate_user(email: str, password: str):
    """Authenticate user with email and password"""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        payload = verify_token(credentials.credentials)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user["last_login"] = datetime.utcnow().isoformat()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "permissions": user["permissions"],
            "is_active": user["is_active"]
        }
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout endpoint"""
    # In a real implementation, you might want to blacklist the token
    # For now, we'll just return success
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserInfo(
        id=current_user["id"],
        email=current_user["email"],
        username=current_user["username"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        permissions=current_user["permissions"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
        last_login=current_user["last_login"]
    )


@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user["email"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/validate")
async def validate_token(current_user: dict = Depends(get_current_user)):
    """Validate current token"""
    return {
        "valid": True,
        "user": {
            "id": current_user["id"],
            "email": current_user["email"],
            "username": current_user["username"],
            "role": current_user["role"]
        }
    }
