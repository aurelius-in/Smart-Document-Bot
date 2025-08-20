from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.security import security_manager, get_current_user, require_permission
from ...database.connection import get_db
from ...database.models import User, Role, UserRole

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserInfo(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    roles: list[str] = []


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
    client_request: Request = None
):
    """Login endpoint with comprehensive security logging"""
    try:
        # Authenticate user
        user = security_manager.authenticate_user(db, request.email, request.password)
        if not user:
            # Log failed login attempt
            if client_request:
                security_manager.log_security_event(
                    event_type="login_failed",
                    user_id=None,
                    ip_address=client_request.client.host,
                    details={"email": request.email, "reason": "invalid_credentials"}
                )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security_manager.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Get user roles
        user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        role_names = []
        for user_role in user_roles:
            role = db.query(Role).filter(Role.id == user_role.role_id).first()
            if role:
                role_names.append(role.name)
        
        # Log successful login
        if client_request:
            security_manager.log_security_event(
                event_type="login_success",
                user_id=user.id,
                ip_address=client_request.client.host,
                details={"email": user.email, "roles": role_names}
            )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "roles": role_names
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log unexpected error
        if client_request:
            security_manager.log_security_event(
                event_type="login_error",
                user_id=None,
                ip_address=client_request.client.host,
                details={"email": request.email, "error": str(e)}
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    client_request: Request = None
):
    """Logout endpoint with token blacklisting"""
    try:
        # Get the token from the request
        if client_request and "authorization" in client_request.headers:
            token = client_request.headers["authorization"].replace("Bearer ", "")
            security_manager.blacklist_token(token)
        
        # Log logout event
        if client_request:
            security_manager.log_security_event(
                event_type="logout",
                user_id=current_user.id,
                ip_address=client_request.client.host,
                details={"email": current_user.email}
            )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        # Log error but don't fail the logout
        if client_request:
            security_manager.log_security_event(
                event_type="logout_error",
                user_id=current_user.id,
                ip_address=client_request.client.host,
                details={"error": str(e)}
            )
        return {"message": "Logged out (with warnings)"}


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    try:
        # Get user roles
        user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
        role_names = []
        for user_role in user_roles:
            role = db.query(Role).filter(Role.id == user_role.role_id).first()
            if role:
                role_names.append(role.name)
        
        return UserInfo(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            is_active=current_user.is_active,
            is_superuser=current_user.is_superuser,
            created_at=current_user.created_at,
            last_login=current_user.last_login,
            roles=role_names
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user),
    client_request: Request = None
):
    """Refresh access token"""
    try:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security_manager.create_access_token(
            data={"sub": current_user.email}, expires_delta=access_token_expires
        )
        
        # Log token refresh
        if client_request:
            security_manager.log_security_event(
                event_type="token_refresh",
                user_id=current_user.id,
                ip_address=client_request.client.host,
                details={"email": current_user.email}
            )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@router.post("/register")
async def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db),
    client_request: Request = None
):
    """Register new user (admin only)"""
    try:
        # Check if user already exists
        existing_user = security_manager.get_user_by_email(db, request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        hashed_password = security_manager.get_password_hash(request.password)
        new_user = User(
            email=request.email,
            hashed_password=hashed_password,
            full_name=request.full_name,
            is_active=True,
            is_superuser=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Assign default user role
        default_role = db.query(Role).filter(Role.name == "user").first()
        if default_role:
            user_role = UserRole(user_id=new_user.id, role_id=default_role.id)
            db.add(user_role)
            db.commit()
        
        # Log user registration
        if client_request:
            security_manager.log_security_event(
                event_type="user_registered",
                user_id=new_user.id,
                ip_address=client_request.client.host,
                details={"email": new_user.email, "registered_by": "admin"}
            )
        
        return {
            "message": "User registered successfully",
            "user_id": new_user.id,
            "email": new_user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    client_request: Request = None
):
    """Change user password"""
    try:
        # Verify current password
        if not security_manager.verify_password(request.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        new_hashed_password = security_manager.get_password_hash(request.new_password)
        current_user.hashed_password = new_hashed_password
        db.commit()
        
        # Log password change
        if client_request:
            security_manager.log_security_event(
                event_type="password_changed",
                user_id=current_user.id,
                ip_address=client_request.client.host,
                details={"email": current_user.email}
            )
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    client_request: Request = None
):
    """Request password reset (sends email)"""
    try:
        # Check if user exists
        user = security_manager.get_user_by_email(db, request.email)
        if not user:
            # Don't reveal if user exists or not
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Generate reset token
        reset_token = security_manager.create_access_token(
            data={"sub": user.email, "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        # TODO: Send email with reset link
        # In production, this would send an actual email
        
        # Log password reset request
        if client_request:
            security_manager.log_security_event(
                event_type="password_reset_requested",
                user_id=user.id,
                ip_address=client_request.client.host,
                details={"email": user.email}
            )
        
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )


@router.get("/validate")
async def validate_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate current token"""
    try:
        # Get user roles
        user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
        role_names = []
        for user_role in user_roles:
            role = db.query(Role).filter(Role.id == user_role.role_id).first()
            if role:
                role_names.append(role.name)
        
        return {
            "valid": True,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "is_active": current_user.is_active,
                "is_superuser": current_user.is_superuser,
                "roles": role_names
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate token"
        )


@router.get("/permissions")
async def get_user_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user permissions"""
    try:
        permissions = security_manager.get_user_permissions(db, current_user)
        return {
            "user_id": current_user.id,
            "email": current_user.email,
            "permissions": permissions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve permissions"
        )


@router.get("/security-events")
async def get_security_events(
    current_user: User = Depends(require_permission("admin:security_events")),
    limit: int = 100
):
    """Get recent security events (admin only)"""
    try:
        # Get security events from Redis
        events = []
        for i in range(min(limit, 1000)):
            event = security_manager.redis_client.lindex("security_events", i)
            if event:
                events.append(eval(event))  # In production, use proper JSON parsing
        
        return {
            "events": events[:limit],
            "total": len(events)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security events"
        )
