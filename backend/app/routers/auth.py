"""
Authentication Router - /api/auth endpoints
Handles user signup, login, logout, and session management
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
import logging

from app.models.user import (
    UserCreate, 
    UserLogin, 
    UserResponse,
    Token,
    SessionResponse,
    LoginResponse,
    SignupResponse
)
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    require_auth,
    get_user_by_email
)
from app.models.user import TokenData
from app.database import get_users_collection, get_user_stats_collection

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """
    Register a new user.
    
    - Creates user with hashed password
    - Initializes user stats
    - Returns JWT token for immediate login
    """
    users = get_users_collection()
    user_stats = get_user_stats_collection()
    
    # Check if email already exists
    existing_user = await users.find_one({"email": user_data.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user document
    now = datetime.utcnow()
    user_doc = {
        "name": user_data.name,
        "email": user_data.email.lower(),
        "password": get_password_hash(user_data.password),
        "role": "user",
        "provider": "credentials",
        "createdAt": now,
        "updatedAt": now
    }
    
    # Insert user
    result = await users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Initialize user stats
    stats_doc = {
        "userId": result.inserted_id,
        "questionsAsked": 0,
        "topicsLearned": [],
        "totalAccuracy": 0,
        "accuracyCount": 0,
        "lastActiveDate": now,
        "streak": 0,
        "coursesEnrolled": [],
        "createdAt": now,
        "updatedAt": now
    }
    await user_stats.insert_one(stats_doc)
    
    # Create JWT token
    token = create_access_token({
        "id": user_id,
        "name": user_data.name,
        "email": user_data.email.lower(),
        "role": "user"
    })
    
    logger.info(f"New user registered: {user_data.email}")
    
    return SignupResponse(
        message="User created successfully",
        token=token,
        user=UserResponse(
            _id=user_id,
            name=user_data.name,
            email=user_data.email.lower(),
            role="user",
            provider="credentials",
            createdAt=now
        )
    )


@router.post("/login", response_model=LoginResponse)
async def login(credentials: UserLogin):
    """
    Authenticate user and return JWT token.
    
    - Validates email and password
    - Returns JWT token and user data
    """
    users = get_users_collection()
    
    # Find user by email
    user = await users.find_one({"email": credentials.email.lower()})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create JWT token
    token = create_access_token({
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user.get("role", "user")
    })
    
    logger.info(f"User logged in: {credentials.email}")
    
    return LoginResponse(
        token=token,
        user=UserResponse(
            _id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            role=user.get("role", "user"),
            image=user.get("image"),
            provider=user.get("provider", "credentials"),
            createdAt=user.get("createdAt")
        )
    )


@router.post("/logout")
async def logout(current_user: TokenData = Depends(require_auth)):
    """
    Logout current user.
    
    Note: Since we use stateless JWT tokens, logout is handled client-side
    by removing the token. This endpoint is for API completeness.
    """
    logger.info(f"User logged out: {current_user.email}")
    
    return {"message": "Logged out successfully"}


@router.get("/session", response_model=SessionResponse)
async def get_session(current_user: TokenData = Depends(get_current_user)):
    """
    Get current session/user information.
    
    - Returns authenticated user data if valid token
    - Returns authenticated: false if no token or invalid token
    """
    if current_user is None:
        return SessionResponse(authenticated=False, user=None)
    
    # Get full user data from database
    users = get_users_collection()
    user = await users.find_one({"_id": ObjectId(current_user.id)})
    
    if not user:
        return SessionResponse(authenticated=False, user=None)
    
    return SessionResponse(
        authenticated=True,
        user=UserResponse(
            _id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            role=user.get("role", "user"),
            image=user.get("image"),
            provider=user.get("provider", "credentials"),
            createdAt=user.get("createdAt")
        )
    )
