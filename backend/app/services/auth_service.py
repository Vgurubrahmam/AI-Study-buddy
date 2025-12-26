"""
Authentication Service - JWT token management and password hashing
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.config import settings
from app.models.user import TokenData, UserResponse
from app.database import get_users_collection

logger = logging.getLogger(__name__)

# Password hashing context (bcrypt with 10 rounds to match frontend)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing token payload (id, name, email)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.jwt_expiration_days)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData if valid, None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        
        user_id = payload.get("id")
        name = payload.get("name")
        email = payload.get("email")
        role = payload.get("role", "user")
        
        if user_id is None or email is None:
            return None
            
        return TokenData(id=user_id, name=name, email=email, role=role)
        
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[TokenData]:
    """
    Dependency to get current user from JWT token.
    Returns None if no valid token provided (allows optional auth).
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header
        
    Returns:
        TokenData if authenticated, None otherwise
    """
    if credentials is None:
        return None
        
    token = credentials.credentials
    token_data = decode_token(token)
    
    return token_data


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenData:
    """
    Dependency to require authentication.
    Raises 401 if not authenticated.
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header
        
    Returns:
        TokenData for authenticated user
        
    Raises:
        HTTPException: 401 if not authenticated
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    token_data = decode_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return token_data


async def require_admin(
    current_user: TokenData = Depends(require_auth)
) -> TokenData:
    """
    Dependency to require admin role.
    Raises 403 if not admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        TokenData for admin user
        
    Raises:
        HTTPException: 403 if not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


async def get_user_from_db(user_id: str) -> Optional[dict]:
    """
    Get user from database by ID.
    
    Args:
        user_id: User's ObjectId string
        
    Returns:
        User document if found, None otherwise
    """
    from bson import ObjectId
    
    try:
        users = get_users_collection()
        user = await users.find_one({"_id": ObjectId(user_id)})
        return user
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None


async def get_user_by_email(email: str) -> Optional[dict]:
    """
    Get user from database by email.
    
    Args:
        email: User's email address
        
    Returns:
        User document if found, None otherwise
    """
    try:
        users = get_users_collection()
        user = await users.find_one({"email": email.lower()})
        return user
    except Exception as e:
        logger.error(f"Error fetching user by email: {e}")
        return None
