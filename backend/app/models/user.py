"""
User Models - Pydantic schemas for user-related operations
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class UserBase(BaseModel):
    """Base user model with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """Model for user registration"""
    password: str = Field(..., min_length=6, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }


class UserResponse(BaseModel):
    """Model for user response (excludes sensitive data)"""
    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    role: Literal["user", "admin"] = "user"
    image: Optional[str] = None
    provider: Literal["credentials", "google"] = "credentials"
    createdAt: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "John Doe",
                "email": "john@example.com",
                "role": "user",
                "provider": "credentials"
            }
        }


class UserInDB(UserBase):
    """Model for user stored in database"""
    id: Optional[str] = Field(None, alias="_id")
    password: str
    role: Literal["user", "admin"] = "user"
    image: Optional[str] = None
    provider: Literal["credentials", "google"] = "credentials"
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class Token(BaseModel):
    """JWT Token response model"""
    token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """Token payload data"""
    id: str
    name: str
    email: EmailStr
    role: Optional[str] = "user"


class SessionResponse(BaseModel):
    """Session check response"""
    authenticated: bool
    user: Optional[UserResponse] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "authenticated": True,
                "user": {
                    "_id": "507f1f77bcf86cd799439011",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "user"
                }
            }
        }


class LoginResponse(BaseModel):
    """Login response with token and user"""
    token: str
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "_id": "507f1f77bcf86cd799439011",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "user"
                }
            }
        }


class SignupResponse(BaseModel):
    """Signup response"""
    message: str
    user: UserResponse
    token: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "User created successfully",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "_id": "507f1f77bcf86cd799439011",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "user"
                }
            }
        }
