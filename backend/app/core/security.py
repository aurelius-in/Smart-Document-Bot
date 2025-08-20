import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import redis
import hashlib
import secrets
import logging

from .config import settings
from ..database.connection import get_db
from ..database.models import User, Role, UserRole

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
security = HTTPBearer()

# Redis for token blacklisting and rate limiting
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

# Security logging
logger = logging.getLogger(__name__)

class SecurityManager:
    """Comprehensive security management for the application"""
    
    def __init__(self):
        self.rate_limit_window = 3600  # 1 hour
        self.max_requests_per_window = 1000
        self.token_blacklist_prefix = "blacklist:"
        self.rate_limit_prefix = "rate_limit:"
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email from database"""
        return db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID from database"""
        return db.query(User).filter(User.id == user_id).first()
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password"""
        user = self.get_user_by_email(db, email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32)  # JWT ID for blacklisting
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            # Check if token is blacklisted
            if self.is_token_blacklisted(token):
                return None
            
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
                return None
            
            return payload
        except JWTError:
            return None
    
    def blacklist_token(self, token: str, expires_in: int = 3600) -> bool:
        """Add token to blacklist"""
        try:
            # Hash the token for storage
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            redis_client.setex(
                f"{self.token_blacklist_prefix}{token_hash}",
                expires_in,
                "blacklisted"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            return redis_client.exists(f"{self.token_blacklist_prefix}{token_hash}") > 0
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False
    
    def check_rate_limit(self, identifier: str) -> bool:
        """Check rate limiting for an identifier (IP or user)"""
        try:
            key = f"{self.rate_limit_prefix}{identifier}"
            current_requests = redis_client.get(key)
            
            if current_requests is None:
                redis_client.setex(key, self.rate_limit_window, 1)
                return True
            
            current_requests = int(current_requests)
            if current_requests >= self.max_requests_per_window:
                return False
            
            redis_client.incr(key)
            return True
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow if Redis fails
    
    def get_user_permissions(self, db: Session, user: User) -> List[str]:
        """Get user permissions from database"""
        try:
            user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
            permissions = []
            
            for user_role in user_roles:
                role = db.query(Role).filter(Role.id == user_role.role_id).first()
                if role and role.permissions:
                    if isinstance(role.permissions, list):
                        permissions.extend(role.permissions)
                    elif isinstance(role.permissions, dict):
                        permissions.extend(role.permissions.get("permissions", []))
            
            return list(set(permissions))  # Remove duplicates
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return []
    
    def has_permission(self, db: Session, user: User, permission: str) -> bool:
        """Check if user has a specific permission"""
        try:
            # Superuser has all permissions
            if user.is_superuser:
                return True
            
            user_permissions = self.get_user_permissions(db, user)
            
            # Check for wildcard permission
            if "*" in user_permissions:
                return True
            
            # Check for specific permission
            if permission in user_permissions:
                return True
            
            # Check for role-based permissions
            if permission.startswith("role:"):
                required_role = permission.split(":")[1]
                user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
                for user_role in user_roles:
                    role = db.query(Role).filter(Role.id == user_role.role_id).first()
                    if role and role.name == required_role:
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    def log_security_event(self, event_type: str, user_id: Optional[int], 
                          ip_address: str, details: Dict[str, Any]) -> None:
        """Log security events"""
        try:
            event_data = {
                "event_type": event_type,
                "user_id": user_id,
                "ip_address": ip_address,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details
            }
            
            # Log to application logs
            logger.info(f"Security event: {event_data}")
            
            # Store in Redis for monitoring
            redis_client.lpush("security_events", str(event_data))
            redis_client.ltrim("security_events", 0, 999)  # Keep last 1000 events
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")


# Global security manager instance
security_manager = SecurityManager()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        payload = security_manager.verify_token(token)
        
        if payload is None:
            raise credentials_exception
            
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = security_manager.get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
        
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Get the current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def require_permission(permission: str):
    """Decorator to require a specific permission"""
    def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not security_manager.has_permission(db, current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    
    return permission_dependency


def rate_limit_middleware(request: Request, db: Session = Depends(get_db)):
    """Rate limiting middleware"""
    # Get client IP
    client_ip = request.client.host
    
    # Check rate limit
    if not security_manager.check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return True


def log_security_event_middleware(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    """Log security events middleware"""
    client_ip = request.client.host
    
    # Log the request
    security_manager.log_security_event(
        event_type="api_request",
        user_id=current_user.id if current_user else None,
        ip_address=client_ip,
        details={
            "method": request.method,
            "path": request.url.path,
            "user_agent": request.headers.get("user-agent", ""),
            "referer": request.headers.get("referer", "")
        }
    )
    
    return True


# Backward compatibility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return security_manager.verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return security_manager.get_password_hash(password)


def get_user_by_email(email: str):
    """Get user by email (deprecated - use database session)"""
    logger.warning("get_user_by_email called without database session - use database models directly")
    return None


def authenticate_user(email: str, password: str):
    """Authenticate user (deprecated - use database session)"""
    logger.warning("authenticate_user called without database session - use SecurityManager.authenticate_user")
    return None


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    return security_manager.create_access_token(data, expires_delta)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    return security_manager.verify_token(token)


async def get_current_user_legacy(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Legacy get_current_user function (deprecated)"""
    logger.warning("get_current_user_legacy called - use get_current_user with database session")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Legacy authentication not supported"
    )


def has_permission(user: Dict[str, Any], permission: str) -> bool:
    """Check if user has a specific permission (deprecated)"""
    logger.warning("has_permission called with dict user - use SecurityManager.has_permission with User model")
    return False


def require_permission_legacy(permission: str):
    """Legacy permission decorator (deprecated)"""
    def permission_dependency(current_user: Dict[str, Any] = Depends(get_current_user_legacy)):
        logger.warning("require_permission_legacy called - use require_permission with database session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Legacy permission system not supported"
        )
    
    return permission_dependency