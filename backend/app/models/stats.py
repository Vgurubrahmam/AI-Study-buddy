"""
Stats Models - Pydantic schemas for statistics and analytics
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class TopUser(BaseModel):
    """Model for top user statistics"""
    id: str = Field(..., alias="_id")
    count: int
    name: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        populate_by_name = True


class AdminStats(BaseModel):
    """Model for admin dashboard statistics"""
    totalUsers: int = 0
    totalCourses: int = 0
    totalChats: int = 0
    chatsToday: int = 0
    chatsThisWeek: int = 0
    chatsThisMonth: int = 0
    topUsers: List[TopUser] = Field(default_factory=list)
    averageChatsPerUser: float = 0.0
    newUsersToday: int = 0
    newUsersThisWeek: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "totalUsers": 150,
                "totalCourses": 12,
                "totalChats": 5420,
                "chatsToday": 127,
                "chatsThisWeek": 850,
                "chatsThisMonth": 3200,
                "topUsers": [
                    {"_id": "507f1f77bcf86cd799439011", "count": 45, "name": "John"}
                ],
                "averageChatsPerUser": 36.1,
                "newUsersToday": 5,
                "newUsersThisWeek": 25
            }
        }


class StatsResponse(BaseModel):
    """Response wrapper for stats"""
    stats: AdminStats


class UserStats(BaseModel):
    """Model for individual user statistics"""
    id: Optional[str] = Field(None, alias="_id")
    userId: str
    questionsAsked: int = 0
    topicsLearned: List[str] = Field(default_factory=list)
    totalAccuracy: float = 0.0
    accuracyCount: int = 0
    lastActiveDate: Optional[datetime] = None
    streak: int = 0
    coursesEnrolled: List[str] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "userId": "507f1f77bcf86cd799439012",
                "questionsAsked": 150,
                "topicsLearned": ["Machine Learning", "Python", "Statistics"],
                "totalAccuracy": 85.5,
                "accuracyCount": 50,
                "lastActiveDate": "2024-12-21T10:00:00Z",
                "streak": 7,
                "coursesEnrolled": ["course1", "course2"]
            }
        }


class UserStatsUpdate(BaseModel):
    """Model for updating user statistics"""
    questionsAsked: Optional[int] = None
    topicsLearned: Optional[List[str]] = None
    totalAccuracy: Optional[float] = None
    accuracyCount: Optional[int] = None
    streak: Optional[int] = None
    coursesEnrolled: Optional[List[str]] = None


class DashboardData(BaseModel):
    """Model for user dashboard data"""
    questionsAsked: int = 0
    streak: int = 0
    coursesEnrolled: int = 0
    averageAccuracy: float = 0.0
    recentTopics: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "questionsAsked": 150,
                "streak": 7,
                "coursesEnrolled": 3,
                "averageAccuracy": 85.5,
                "recentTopics": ["Neural Networks", "Python", "Statistics"]
            }
        }
