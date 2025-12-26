"""
User Router - /api/user endpoints
Handles user-specific operations like chat history
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime
from bson import ObjectId
from typing import Optional
import logging

from app.models.chat import ChatHistoryResponse, ChatHistoryItem
from app.models.user import TokenData
from app.services.auth_service import require_auth
from app.database import get_chat_history_collection, get_user_stats_collection

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/chat-history", response_model=ChatHistoryResponse)
async def get_user_chat_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: TokenData = Depends(require_auth)
):
    """
    Get chat history for the current authenticated user.
    
    - Returns paginated chat history
    - Sorted by most recent first
    """
    chat_history = get_chat_history_collection()
    
    # Calculate skip for pagination
    skip = (page - 1) * limit
    
    # Get total count
    total = await chat_history.count_documents({"userId": ObjectId(current_user.id)})
    
    # Get chat history with pagination
    cursor = chat_history.find(
        {"userId": ObjectId(current_user.id)}
    ).sort("createdAt", -1).skip(skip).limit(limit)
    
    history_items = []
    async for doc in cursor:
        history_items.append(ChatHistoryItem(
            _id=str(doc["_id"]),
            userId=str(doc["userId"]),
            userMessage=doc["userMessage"],
            assistantResponse=doc["assistantResponse"],
            createdAt=doc["createdAt"],
            tokens=doc.get("tokens")
        ))
    
    return ChatHistoryResponse(
        history=history_items,
        total=total,
        page=page,
        limit=limit
    )


@router.delete("/chat-history")
async def delete_user_chat_entry(
    id: str = Query(..., description="Chat history entry ID to delete"),
    current_user: TokenData = Depends(require_auth)
):
    """
    Delete a specific chat history entry for the current user.
    
    - Users can only delete their own chat entries
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
    
    # Find and verify ownership
    entry = await chat_history.find_one({"_id": entry_id})
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat history entry not found"
        )
    
    # Check ownership
    if str(entry["userId"]) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own chat history"
        )
    
    # Delete the entry
    await chat_history.delete_one({"_id": entry_id})
    
    logger.info(f"Chat entry deleted by user {current_user.id}: {id}")
    
    return {"message": "Chat history entry deleted successfully"}


@router.get("/stats")
async def get_user_stats(current_user: TokenData = Depends(require_auth)):
    """
    Get statistics for the current authenticated user.
    
    - Questions asked, streak, courses enrolled, etc.
    """
    user_stats = get_user_stats_collection()
    chat_history = get_chat_history_collection()
    
    # Get user stats
    stats = await user_stats.find_one({"userId": ObjectId(current_user.id)})
    
    # Get actual question count from chat history
    questions_count = await chat_history.count_documents(
        {"userId": ObjectId(current_user.id)}
    )
    
    if stats:
        return {
            "questionsAsked": questions_count,
            "streak": stats.get("streak", 0),
            "coursesEnrolled": len(stats.get("coursesEnrolled", [])),
            "topicsLearned": stats.get("topicsLearned", []),
            "averageAccuracy": (
                stats.get("totalAccuracy", 0) / stats.get("accuracyCount", 1)
                if stats.get("accuracyCount", 0) > 0 else 0
            ),
            "lastActiveDate": stats.get("lastActiveDate")
        }
    
    # Return default stats if none exist
    return {
        "questionsAsked": questions_count,
        "streak": 0,
        "coursesEnrolled": 0,
        "topicsLearned": [],
        "averageAccuracy": 0,
        "lastActiveDate": None
    }


@router.put("/stats")
async def update_user_stats(
    stats_update: dict,
    current_user: TokenData = Depends(require_auth)
):
    """
    Update statistics for the current authenticated user.
    
    - Update streak, topics learned, etc.
    """
    user_stats = get_user_stats_collection()
    
    # Prepare update document
    update_doc = {"updatedAt": datetime.utcnow()}
    
    allowed_fields = [
        "questionsAsked", "topicsLearned", "totalAccuracy",
        "accuracyCount", "streak", "coursesEnrolled", "lastActiveDate"
    ]
    
    for field in allowed_fields:
        if field in stats_update:
            update_doc[field] = stats_update[field]
    
    # Update or insert stats
    result = await user_stats.update_one(
        {"userId": ObjectId(current_user.id)},
        {"$set": update_doc},
        upsert=True
    )
    
    return {"message": "Stats updated successfully"}
