"""
AI Study Buddy Backend - FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, chat, user, admin, db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting AI Study Buddy Backend...")
    await connect_to_mongo()
    logger.info("Connected to MongoDB")
    
    # Lazy load ML model (only when first request comes in)
    logger.info(f"ML Model configured: {settings.model_name}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Study Buddy Backend...")
    await close_mongo_connection()
    logger.info("Disconnected from MongoDB")


# Create FastAPI application
app = FastAPI(
    title="AI Study Buddy API",
    description="""
    🎓 AI Study Buddy Backend API
    
    An intelligent tutoring assistant that provides:
    - 📚 Question answering across subjects
    - 🧠 Adaptive learning support
    - 📊 Progress tracking
    - 🤖 Powered by microsoft/Phi-3-mini-4k-instruct
    
    ## Features
    - **Authentication**: JWT-based auth with signup/login
    - **Chat**: AI-powered Q&A with RAG
    - **Courses**: Course management and enrollment
    - **Progress**: Learning analytics and tracking
    - **Admin**: Dashboard and management tools
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(db.router, prefix="/api/db", tags=["Database"])


@app.get("/", tags=["Root"])
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Study Buddy API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "healthy"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "model": settings.model_name,
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=not settings.is_production
    )
