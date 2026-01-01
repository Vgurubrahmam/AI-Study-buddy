"""
Pydantic Models Package
"""

from app.models.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserInDB,
    Token,
    TokenData,
    SessionResponse
)
from app.models.course import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseInDB
)
from app.models.chat import (
    ChatMessage,
    ChatResponse,
    ChatHistoryItem,
    ChatHistoryResponse
)
from app.models.stats import (
    UserStats,
    AdminStats,
    TopUser
)

__all__ = [
    # User models
    "UserCreate",
    "UserLogin", 
    "UserResponse",
    "UserInDB",
    "Token",
    "TokenData",
    "SessionResponse",
    # Course models
    "CourseCreate",
    "CourseUpdate",
    "CourseResponse",
    "CourseInDB",
    # Chat models
    "ChatMessage",
    "ChatResponse",
    "ChatHistoryItem",
    "ChatHistoryResponse",
    # Stats models
    "UserStats",
    "AdminStats",
    "TopUser",
]
