"""
MongoDB Database Connection and Management
Uses Motor for async MongoDB operations
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """MongoDB Database Manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


# Global database instance
database = Database()


async def connect_to_mongo():
    """
    Connect to MongoDB using Motor async driver.
    Called during application startup.
    """
    try:
        logger.info(f"Connecting to MongoDB...")
        
        database.client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=50,
            minPoolSize=10
        )
        
        # Verify connection
        await database.client.admin.command("ping")
        
        database.db = database.client[settings.database_name]
        
        logger.info(f"Connected to MongoDB database: {settings.database_name}")
        
        # Create indexes
        await create_indexes()
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """
    Close MongoDB connection.
    Called during application shutdown.
    """
    if database.client:
        database.client.close()
        logger.info("Closed MongoDB connection")


async def create_indexes():
    """Create necessary indexes for collections"""
    try:
        db = database.db
        
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        
        # Chat history indexes
        await db.chatHistory.create_index([
            ("userId", 1),
            ("createdAt", -1)
        ])
        await db.chatHistory.create_index("createdAt")
        
        # User stats indexes
        await db.userStats.create_index("userId", unique=True)
        
        # User progress indexes
        await db.userProgress.create_index([
            ("userId", 1),
            ("courseId", 1)
        ], unique=True)
        
        # Courses indexes
        await db.courses.create_index("category")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Error creating indexes: {e}")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance for dependency injection.
    
    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
    """
    if database.db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return database.db


# Collection helpers
def get_users_collection():
    """Get users collection"""
    return get_database().users


def get_courses_collection():
    """Get courses collection"""
    return get_database().courses


def get_chat_history_collection():
    """Get chat history collection"""
    return get_database().chatHistory


def get_user_stats_collection():
    """Get user stats collection"""
    return get_database().userStats


def get_user_progress_collection():
    """Get user progress collection"""
    return get_database().userProgress
