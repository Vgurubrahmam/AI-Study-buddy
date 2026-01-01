"""
Course Models - Pydantic schemas for course-related operations
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime


class CourseBase(BaseModel):
    """Base course model with common fields"""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    difficulty: Literal["Beginner", "Intermediate", "Advanced"] = "Beginner"
    icon: str = Field(default="📚", max_length=10)
    category: str = Field(..., min_length=1, max_length=100)


class CourseCreate(CourseBase):
    """Model for creating a new course"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Introduction to Machine Learning",
                "description": "Learn the fundamentals of machine learning algorithms and applications.",
                "difficulty": "Beginner",
                "icon": "🤖",
                "category": "Computer Science"
            }
        }


class CourseUpdate(BaseModel):
    """Model for updating a course (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    difficulty: Optional[Literal["Beginner", "Intermediate", "Advanced"]] = None
    icon: Optional[str] = Field(None, max_length=10)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Advanced Machine Learning",
                "difficulty": "Advanced"
            }
        }


class CourseResponse(CourseBase):
    """Model for course response"""
    id: str = Field(..., alias="_id")
    enrolledCount: int = 0
    rating: float = 0.0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Introduction to Machine Learning",
                "description": "Learn the fundamentals of machine learning.",
                "difficulty": "Beginner",
                "icon": "🤖",
                "category": "Computer Science",
                "enrolledCount": 150,
                "rating": 4.5
            }
        }


class CourseInDB(CourseBase):
    """Model for course stored in database"""
    id: Optional[str] = Field(None, alias="_id")
    enrolledCount: int = 0
    rating: float = 0.0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class CoursesListResponse(BaseModel):
    """Response model for list of courses"""
    courses: List[CourseResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "courses": [
                    {
                        "_id": "507f1f77bcf86cd799439011",
                        "name": "Machine Learning",
                        "description": "Learn ML fundamentals",
                        "difficulty": "Beginner",
                        "icon": "🤖",
                        "category": "Computer Science",
                        "enrolledCount": 150,
                        "rating": 4.5
                    }
                ],
                "total": 1
            }
        }


class UserProgress(BaseModel):
    """Model for tracking user progress in a course"""
    id: Optional[str] = Field(None, alias="_id")
    userId: str
    courseId: str
    progress: float = Field(default=0.0, ge=0, le=100)
    completedModules: List[str] = Field(default_factory=list)
    lastAccessed: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "userId": "507f1f77bcf86cd799439012",
                "courseId": "507f1f77bcf86cd799439013",
                "progress": 45.5,
                "completedModules": ["module1", "module2"],
                "lastAccessed": "2024-12-21T10:00:00Z"
            }
        }
