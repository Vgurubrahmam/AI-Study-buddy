"""
Chat Models - Pydantic schemas for chat-related operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TokenUsage(BaseModel):
    """Model for token usage tracking"""
    input: int = 0
    output: int = 0


class ChatMessage(BaseModel):
    """Model for incoming chat message"""
    message: str = Field(..., min_length=1, max_length=10000)
    userId: Optional[str] = None
    courseId: Optional[str] = None  # Optional context for course-specific questions
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Explain the concept of neural networks",
                "userId": "507f1f77bcf86cd799439011",
                "courseId": "507f1f77bcf86cd799439012"
            }
        }


class ChatResponse(BaseModel):
    """Model for chat response"""
    response: str
    tokens: Optional[TokenUsage] = None
    model: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Neural networks are computational models inspired by biological neural networks...",
                "tokens": {
                    "input": 15,
                    "output": 250
                },
                "model": "phi-3-mini-4k-instruct"
            }
        }


class ChatHistoryItem(BaseModel):
    """Model for a single chat history entry"""
    id: str = Field(..., alias="_id")
    userId: str
    userMessage: str
    assistantResponse: str
    createdAt: datetime
    tokens: Optional[TokenUsage] = None
    userName: Optional[str] = None  # For admin view
    userEmail: Optional[str] = None  # For admin view
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "userId": "507f1f77bcf86cd799439012",
                "userMessage": "What is machine learning?",
                "assistantResponse": "Machine learning is a subset of AI...",
                "createdAt": "2024-12-21T10:00:00Z",
                "tokens": {
                    "input": 10,
                    "output": 150
                }
            }
        }


class ChatHistoryResponse(BaseModel):
    """Response model for chat history list"""
    history: List[ChatHistoryItem]
    total: int
    page: int = 1
    limit: int = 50
    
    class Config:
        json_schema_extra = {
            "example": {
                "history": [
                    {
                        "_id": "507f1f77bcf86cd799439011",
                        "userId": "507f1f77bcf86cd799439012",
                        "userMessage": "What is machine learning?",
                        "assistantResponse": "Machine learning is...",
                        "createdAt": "2024-12-21T10:00:00Z"
                    }
                ],
                "total": 100,
                "page": 1,
                "limit": 50
            }
        }


class ChatHistoryCreate(BaseModel):
    """Model for creating chat history entry"""
    userId: str
    userMessage: str
    assistantResponse: str
    tokens: Optional[TokenUsage] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class StreamingChunk(BaseModel):
    """Model for streaming response chunks"""
    content: str
    done: bool = False
    error: Optional[str] = None
