"""
Database Router - /api/db endpoints
Handles database initialization and management
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging

from app.database import get_database, create_indexes

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/init")
async def initialize_database():
    """
    Initialize database collections and indexes.
    
    - Creates necessary indexes
    - Sets up default data if needed
    - Safe to run multiple times (idempotent)
    """
    try:
        db = get_database()
        
        # Create indexes
        await create_indexes()
        
        # Check if default admin exists
        users = db.users
        admin = await users.find_one({"role": "admin"})
        
        # Create collections if they don't exist
        collections = await db.list_collection_names()
        
        required_collections = [
            "users", "courses", "chatHistory", 
            "userStats", "userProgress"
        ]
        
        created = []
        for coll in required_collections:
            if coll not in collections:
                await db.create_collection(coll)
                created.append(coll)
        
        # Add some default courses if none exist
        courses = db.courses
        course_count = await courses.count_documents({})
        
        default_courses_added = 0
        if course_count == 0:
            default_courses = [
                {
                    "name": "Introduction to Machine Learning",
                    "description": "Learn the fundamentals of machine learning, including supervised and unsupervised learning, neural networks, and practical applications.",
                    "difficulty": "Beginner",
                    "icon": "🤖",
                    "category": "Computer Science",
                    "enrolledCount": 0,
                    "rating": 0,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Data Science Fundamentals",
                    "description": "Master the essential skills of data science including data analysis, visualization, and statistical methods.",
                    "difficulty": "Beginner",
                    "icon": "📊",
                    "category": "Data Science",
                    "enrolledCount": 0,
                    "rating": 0,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Python Programming",
                    "description": "Comprehensive Python programming course covering basics to advanced concepts like OOP, decorators, and async programming.",
                    "difficulty": "Beginner",
                    "icon": "🐍",
                    "category": "Programming",
                    "enrolledCount": 0,
                    "rating": 0,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Deep Learning",
                    "description": "Advanced course on deep learning covering CNNs, RNNs, Transformers, and state-of-the-art architectures.",
                    "difficulty": "Advanced",
                    "icon": "🧠",
                    "category": "Computer Science",
                    "enrolledCount": 0,
                    "rating": 0,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Natural Language Processing",
                    "description": "Learn NLP techniques including text processing, sentiment analysis, and language models.",
                    "difficulty": "Intermediate",
                    "icon": "💬",
                    "category": "Computer Science",
                    "enrolledCount": 0,
                    "rating": 0,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            ]
            
            await courses.insert_many(default_courses)
            default_courses_added = len(default_courses)
        
        logger.info("Database initialized successfully")
        
        return {
            "message": "Database initialized successfully",
            "collectionsCreated": created,
            "defaultCoursesAdded": default_courses_added,
            "indexesCreated": True,
            "adminExists": admin is not None
        }
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database initialization failed: {str(e)}"
        )


@router.get("/health")
async def database_health():
    """
    Check database connection health.
    """
    try:
        db = get_database()
        
        # Ping the database
        await db.command("ping")
        
        # Get collection stats
        collections = await db.list_collection_names()
        
        stats = {}
        for coll in collections:
            count = await db[coll].count_documents({})
            stats[coll] = count
        
        return {
            "status": "healthy",
            "database": db.name,
            "collections": stats
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unhealthy: {str(e)}"
        )
