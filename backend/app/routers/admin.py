"""
Admin Router - /api/admin endpoints
Handles administrative operations like course management and statistics
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional, List
import logging

from app.models.course import (
    CourseCreate, 
    CourseUpdate, 
    CourseResponse,
    CoursesListResponse
)
from app.models.chat import ChatHistoryResponse, ChatHistoryItem
from app.models.stats import AdminStats, StatsResponse, TopUser
from app.models.user import TokenData
from app.services.auth_service import require_auth, require_admin
from app.database import (
    get_courses_collection,
    get_chat_history_collection,
    get_users_collection,
    get_user_stats_collection
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== COURSES ====================

@router.get("/courses", response_model=CoursesListResponse)
async def get_all_courses(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    current_user: TokenData = Depends(require_auth)
):
    """
    Get all courses (admin or user view).
    
    - Returns list of all courses
    - Optional filtering by category and difficulty
    """
    courses = get_courses_collection()
    
    # Build query filter
    query = {}
    if category:
        query["category"] = category
    if difficulty:
        query["difficulty"] = difficulty
    
    # Get courses
    cursor = courses.find(query).sort("createdAt", -1)
    
    course_list = []
    async for doc in cursor:
        course_list.append(CourseResponse(
            _id=str(doc["_id"]),
            name=doc["name"],
            description=doc["description"],
            difficulty=doc["difficulty"],
            icon=doc.get("icon", "📚"),
            category=doc["category"],
            enrolledCount=doc.get("enrolledCount", 0),
            rating=doc.get("rating", 0),
            createdAt=doc.get("createdAt"),
            updatedAt=doc.get("updatedAt")
        ))
    
    return CoursesListResponse(courses=course_list, total=len(course_list))


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: TokenData = Depends(require_admin)
):
    """
    Create a new course (admin only).
    
    - Requires admin role
    - Creates course with default enrolled count and rating
    """
    courses = get_courses_collection()
    
    now = datetime.utcnow()
    course_doc = {
        "name": course_data.name,
        "description": course_data.description,
        "difficulty": course_data.difficulty,
        "icon": course_data.icon,
        "category": course_data.category,
        "enrolledCount": 0,
        "rating": 0,
        "createdAt": now,
        "updatedAt": now
    }
    
    result = await courses.insert_one(course_doc)
    
    logger.info(f"Course created by admin {current_user.id}: {course_data.name}")
    
    return CourseResponse(
        _id=str(result.inserted_id),
        **course_data.model_dump(),
        enrolledCount=0,
        rating=0,
        createdAt=now,
        updatedAt=now
    )


@router.put("/courses", response_model=CourseResponse)
async def update_course(
    id: str = Query(..., description="Course ID to update"),
    course_update: CourseUpdate = None,
    current_user: TokenData = Depends(require_admin)
):
    """
    Update an existing course (admin only).
    
    - Requires admin role
    - Only updates provided fields
    """
    courses = get_courses_collection()
    
    # Validate ObjectId
    try:
        course_id = ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course ID"
        )
    
    # Check course exists
    existing = await courses.find_one({"_id": course_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Build update document
    update_data = course_update.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )
    
    update_data["updatedAt"] = datetime.utcnow()
    
    # Update course
    await courses.update_one({"_id": course_id}, {"$set": update_data})
    
    # Get updated course
    updated = await courses.find_one({"_id": course_id})
    
    logger.info(f"Course updated by admin {current_user.id}: {id}")
    
    return CourseResponse(
        _id=str(updated["_id"]),
        name=updated["name"],
        description=updated["description"],
        difficulty=updated["difficulty"],
        icon=updated.get("icon", "📚"),
        category=updated["category"],
        enrolledCount=updated.get("enrolledCount", 0),
        rating=updated.get("rating", 0),
        createdAt=updated.get("createdAt"),
        updatedAt=updated.get("updatedAt")
    )


@router.delete("/courses")
async def delete_course(
    id: str = Query(..., description="Course ID to delete"),
    current_user: TokenData = Depends(require_admin)
):
    """
    Delete a course (admin only).
    
    - Requires admin role
    - Permanently deletes the course
    """
    courses = get_courses_collection()
    
    # Validate ObjectId
    try:
        course_id = ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course ID"
        )
    
    # Check course exists
    existing = await courses.find_one({"_id": course_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Delete course
    await courses.delete_one({"_id": course_id})
    
    logger.info(f"Course deleted by admin {current_user.id}: {id}")
    
    return {"message": "Course deleted successfully"}


# ==================== CHAT HISTORY ====================

@router.get("/chat-history", response_model=ChatHistoryResponse)
async def get_all_chat_history(
    userId: Optional[str] = Query(None, description="Filter by user ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: TokenData = Depends(require_admin)
):
    """
    Get all chat history (admin only).
    
    - Requires admin role
    - Can filter by specific user
    - Includes user information
    """
    chat_history = get_chat_history_collection()
    users = get_users_collection()
    
    # Build query
    query = {}
    if userId:
        try:
            query["userId"] = ObjectId(userId)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
    
    # Calculate pagination
    skip = (page - 1) * limit
    total = await chat_history.count_documents(query)
    
    # Get chat history with user info via aggregation
    pipeline = [
        {"$match": query},
        {"$sort": {"createdAt": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "users",
                "localField": "userId",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}}
    ]
    
    history_items = []
    async for doc in chat_history.aggregate(pipeline):
        user_data = doc.get("user", {})
        history_items.append(ChatHistoryItem(
            _id=str(doc["_id"]),
            userId=str(doc["userId"]),
            userMessage=doc["userMessage"],
            assistantResponse=doc["assistantResponse"],
            createdAt=doc["createdAt"],
            tokens=doc.get("tokens"),
            userName=user_data.get("name"),
            userEmail=user_data.get("email")
        ))
    
    return ChatHistoryResponse(
        history=history_items,
        total=total,
        page=page,
        limit=limit
    )


@router.delete("/chat-history")
async def delete_chat_entry_admin(
    id: str = Query(..., description="Chat history entry ID to delete"),
    current_user: TokenData = Depends(require_admin)
):
    """
    Delete any chat history entry (admin only).
    
    - Requires admin role
    - Can delete any user's chat entry
    """
    chat_history = get_chat_history_collection()
    
    # Validate ObjectId
    try:
        entry_id = ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chat history ID"
        )
    
    # Check entry exists
    entry = await chat_history.find_one({"_id": entry_id})
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat history entry not found"
        )
    
    # Delete entry
    await chat_history.delete_one({"_id": entry_id})
    
    logger.info(f"Chat entry deleted by admin {current_user.id}: {id}")
    
    return {"message": "Chat history entry deleted successfully"}


# ==================== STATISTICS ====================

@router.get("/stats", response_model=StatsResponse)
async def get_admin_stats(current_user: TokenData = Depends(require_admin)):
    """
    Get dashboard statistics (admin only).
    
    - Total users, courses, chats
    - Chats today/this week/this month
    - Top users by activity
    """
    users = get_users_collection()
    courses = get_courses_collection()
    chat_history = get_chat_history_collection()
    
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Count totals
    total_users = await users.count_documents({})
    total_courses = await courses.count_documents({})
    total_chats = await chat_history.count_documents({})
    
    # Count chats by time period
    chats_today = await chat_history.count_documents({"createdAt": {"$gte": today_start}})
    chats_this_week = await chat_history.count_documents({"createdAt": {"$gte": week_start}})
    chats_this_month = await chat_history.count_documents({"createdAt": {"$gte": month_start}})
    
    # New users
    new_users_today = await users.count_documents({"createdAt": {"$gte": today_start}})
    new_users_this_week = await users.count_documents({"createdAt": {"$gte": week_start}})
    
    # Top users by chat count
    top_users_pipeline = [
        {"$group": {"_id": "$userId", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}}
    ]
    
    top_users = []
    async for doc in chat_history.aggregate(top_users_pipeline):
        user_data = doc.get("user", {})
        top_users.append(TopUser(
            _id=str(doc["_id"]),
            count=doc["count"],
            name=user_data.get("name"),
            email=user_data.get("email")
        ))
    
    # Calculate average
    avg_chats_per_user = total_chats / total_users if total_users > 0 else 0
    
    stats = AdminStats(
        totalUsers=total_users,
        totalCourses=total_courses,
        totalChats=total_chats,
        chatsToday=chats_today,
        chatsThisWeek=chats_this_week,
        chatsThisMonth=chats_this_month,
        topUsers=top_users,
        averageChatsPerUser=round(avg_chats_per_user, 2),
        newUsersToday=new_users_today,
        newUsersThisWeek=new_users_this_week
    )
    
    return StatsResponse(stats=stats)
