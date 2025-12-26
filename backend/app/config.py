"""
AI Study Buddy Backend Configuration
Environment variables and settings management
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # Database
    mongodb_uri: str = Field(..., alias="MONGODB_URI")
    database_name: str = Field(default="ai_study_buddy", alias="DATABASE_NAME")
    
    # Authentication
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiration_days: int = Field(default=30, alias="JWT_EXPIRATION_DAYS")
    
    # Google OAuth
    google_client_id: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_SECRET")
    
    # ML Model
    model_name: str = Field(
        default="microsoft/Phi-3-mini-4k-instruct", 
        alias="MODEL_NAME"
    )
    model_path: str = Field(default="./models/phi3-finetuned", alias="MODEL_PATH")
    use_gpu: bool = Field(default=True, alias="USE_GPU")
    max_tokens: int = Field(default=1000, alias="MAX_TOKENS")
    temperature: float = Field(default=0.7, alias="TEMPERATURE")
    use_quantization: bool = Field(default=True, alias="USE_QUANTIZATION")
    
    # Embedding Model
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL"
    )
    
    # Vector Store
    chroma_persist_dir: str = Field(default="./chroma_db", alias="CHROMA_PERSIST_DIR")
    
    # Gemini Fallback
    gemini_api_key_1: Optional[str] = Field(default=None, alias="GEMINI_API_KEY_1")
    gemini_api_key_2: Optional[str] = Field(default=None, alias="GEMINI_API_KEY_2")
    
    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ORIGINS"
    )
    
    # PDF Processing
    study_pdfs_dir: str = Field(default="./study_pdfs", alias="STUDY_PDFS_DIR")
    training_data_dir: str = Field(default="./training_data", alias="TRAINING_DATA_DIR")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Export settings instance for easy import
settings = get_settings()
