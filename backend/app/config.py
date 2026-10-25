from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Placement Analyzer"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"

    # Database
    # Defaults to SQLite for immediate local usability and zero-setup testing,
    # but seamlessly switches to PostgreSQL + pgvector (Supabase or local Postgres)
    DATABASE_URL: str = Field(
        default="sqlite:///./placement_analyzer.db",
        description="Database connection string (SQLite or PostgreSQL with pgvector)"
    )

    # LLM and Embedding Providers
    # Options: "mock" (built-in offline testing), "gemini", "openai"
    LLM_PROVIDER: str = "mock"
    LLM_MODEL: str = "gemini-1.5-flash"
    
    EMBEDDING_PROVIDER: str = "mock"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    EMBEDDING_DIMENSION: int = 768

    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # File uploads
    UPLOAD_MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]

    # Retrieval parameters
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_SIMILARITY_THRESHOLD: float = 0.35
    RETRIEVAL_LEXICAL_WEIGHT: float = 0.4
    RETRIEVAL_VECTOR_WEIGHT: float = 0.6

    # Data Retention (in days, 0 = indefinite for user's account until deleted)
    DOCUMENT_RETENTION_DAYS: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Automatically adjust provider if API keys are set in environment
if os.getenv("GEMINI_API_KEY") and settings.LLM_PROVIDER == "mock":
    settings.LLM_PROVIDER = "gemini"
    settings.EMBEDDING_PROVIDER = "gemini"
elif os.getenv("OPENAI_API_KEY") and settings.LLM_PROVIDER == "mock":
    settings.LLM_PROVIDER = "openai"
    settings.EMBEDDING_PROVIDER = "openai"
    settings.EMBEDDING_MODEL = "text-embedding-3-small"
    settings.EMBEDDING_DIMENSION = 1536
