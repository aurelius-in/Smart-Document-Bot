import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "REDLINE"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/redline"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    PGVECTOR_CONNECTION_STRING: str = "postgresql://user:password@localhost/redline_vector"
    
    # LLM Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # Document Processing
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"]
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    ENABLE_TRACING: bool = True
    
    # OPA
    OPA_URL: str = "http://localhost:8181"
    OPA_POLICIES_DIR: str = "./app/risk/policies"
    
    # Audit
    AUDIT_LOG_DIR: str = "./audit_logs"
    AUDIT_RETENTION_DAYS: int = 365
    
    # Agent Settings
    MAX_AGENT_STEPS: int = 10
    AGENT_TIMEOUT_SECONDS: int = 300
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # PII Redaction
    ENABLE_PII_REDACTION: bool = True
    PII_PATTERNS: List[str] = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.AUDIT_LOG_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
