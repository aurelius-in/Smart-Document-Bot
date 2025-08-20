import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    APP_NAME: str = "AI Document Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Security settings
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # File upload settings
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[".pdf", ".docx", ".txt", ".csv", ".xlsx"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # LLM settings
    LLM_MODEL: str = Field(default="gpt-4", env="LLM_MODEL")
    LLM_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    LLM_TEMPERATURE: float = Field(default=0.1, env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(default=4000, env="LLM_MAX_TOKENS")
    
    # Agent settings
    AGENT_TIMEOUT: int = Field(default=300, env="AGENT_TIMEOUT")  # 5 minutes
    AGENT_MAX_RETRIES: int = Field(default=3, env="AGENT_MAX_RETRIES")
    AGENT_CONFIDENCE_THRESHOLD: float = Field(default=0.7, env="AGENT_CONFIDENCE_THRESHOLD")
    
    # Workflow settings
    WORKFLOW_MAX_STAGES: int = Field(default=10, env="WORKFLOW_MAX_STAGES")
    WORKFLOW_PARALLEL_EXECUTION: bool = Field(default=True, env="WORKFLOW_PARALLEL_EXECUTION")
    WORKFLOW_MONITORING_INTERVAL: int = Field(default=5, env="WORKFLOW_MONITORING_INTERVAL")
    
    # Database settings
    DATABASE_URL: str = Field(default="sqlite:///./smart_doc_bot.db", env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    CHROMA_PERSIST_DIRECTORY: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    
    # Memory settings
    MEMORY_TTL: int = Field(default=3600, env="MEMORY_TTL")  # 1 hour
    MEMORY_MAX_SIZE: int = Field(default=1000, env="MEMORY_MAX_SIZE")
    VECTOR_SIMILARITY_THRESHOLD: float = Field(default=0.8, env="VECTOR_SIMILARITY_THRESHOLD")
    
    # Monitoring settings
    ENABLE_MONITORING: bool = Field(default=True, env="ENABLE_MONITORING")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Audit settings
    AUDIT_ENABLED: bool = Field(default=True, env="AUDIT_ENABLED")
    AUDIT_RETENTION_DAYS: int = Field(default=90, env="AUDIT_RETENTION_DAYS")
    AUDIT_ENCRYPTION_ENABLED: bool = Field(default=False, env="AUDIT_ENCRYPTION_ENABLED")
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def get_agent_config():
    """Get agent configuration"""
    return {
        "TIMEOUT": settings.AGENT_TIMEOUT,
        "MAX_RETRIES": settings.AGENT_MAX_RETRIES,
        "CONFIDENCE_THRESHOLD": settings.AGENT_CONFIDENCE_THRESHOLD,
        "LLM_MODEL": settings.LLM_MODEL,
        "LLM_API_KEY": settings.LLM_API_KEY,
        "LLM_TEMPERATURE": settings.LLM_TEMPERATURE,
        "LLM_MAX_TOKENS": settings.LLM_MAX_TOKENS
    }


def get_workflow_config():
    """Get workflow configuration"""
    return {
        "MAX_STAGES": settings.WORKFLOW_MAX_STAGES,
        "PARALLEL_EXECUTION": settings.WORKFLOW_PARALLEL_EXECUTION,
        "MONITORING_INTERVAL": settings.WORKFLOW_MONITORING_INTERVAL
    }