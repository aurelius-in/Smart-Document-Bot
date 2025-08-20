import os
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class Settings(PydanticBaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    APP_NAME: str = Field(default="AI Document Agent", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Security settings
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Database settings
    DATABASE_URL: str = Field(default="postgresql://user:password@localhost/ai_document_agent", env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    
    # ChromaDB settings
    CHROMA_PERSIST_DIRECTORY: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    CHROMA_COLLECTION_NAME: str = Field(default="documents", env="CHROMA_COLLECTION_NAME")
    
    # File storage settings
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    ALLOWED_FILE_TYPES: List[str] = Field(default=[".pdf", ".docx", ".txt", ".csv", ".xlsx"], env="ALLOWED_FILE_TYPES")
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(default=["http://localhost:3000"], env="ALLOWED_ORIGINS")
    ALLOWED_METHODS: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="ALLOWED_METHODS")
    ALLOWED_HEADERS: List[str] = Field(default=["*"], env="ALLOWED_HEADERS")
    
    # Monitoring settings
    ENABLE_MONITORING: bool = Field(default=True, env="ENABLE_MONITORING")
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    GRAFANA_PORT: int = Field(default=3001, env="GRAFANA_PORT")
    
    # AI/ML settings
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    
    # Agent settings
    AGENT_TIMEOUT: int = Field(default=300, env="AGENT_TIMEOUT")  # 5 minutes
    AGENT_MAX_RETRIES: int = Field(default=3, env="AGENT_MAX_RETRIES")
    AGENT_CONCURRENT_LIMIT: int = Field(default=10, env="AGENT_CONCURRENT_LIMIT")
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = Field(default=1000, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # Audit settings
    AUDIT_LOG_ENABLED: bool = Field(default=True, env="AUDIT_LOG_ENABLED")
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=90, env="AUDIT_LOG_RETENTION_DAYS")
    
    # Email settings (for notifications)
    SMTP_HOST: str = Field(default="", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(default="", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    
    # Backup settings
    BACKUP_ENABLED: bool = Field(default=True, env="BACKUP_ENABLED")
    BACKUP_RETENTION_DAYS: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    BACKUP_SCHEDULE: str = Field(default="0 2 * * *", env="BACKUP_SCHEDULE")  # Daily at 2 AM
    
    # Performance settings
    WORKER_PROCESSES: int = Field(default=4, env="WORKER_PROCESSES")
    MAX_CONCURRENT_REQUESTS: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    
    # Feature flags
    ENABLE_WEBSOCKETS: bool = Field(default=True, env="ENABLE_WEBSOCKETS")
    ENABLE_SSE: bool = Field(default=True, env="ENABLE_SSE")
    ENABLE_REAL_TIME_UPDATES: bool = Field(default=True, env="ENABLE_REAL_TIME_UPDATES")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(",")]
        return v


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def get_agent_config() -> Dict[str, Any]:
    """Get agent-specific configuration"""
    return {
        "timeout": settings.AGENT_TIMEOUT,
        "max_retries": settings.AGENT_MAX_RETRIES,
        "concurrent_limit": settings.AGENT_CONCURRENT_LIMIT,
        "openai_model": settings.OPENAI_MODEL,
        "openai_max_tokens": settings.OPENAI_MAX_TOKENS,
        "chroma_collection": settings.CHROMA_COLLECTION_NAME,
        "chroma_persist_dir": settings.CHROMA_PERSIST_DIRECTORY
    }


def get_workflow_config() -> Dict[str, Any]:
    """Get workflow-specific configuration"""
    return {
        "max_file_size": settings.MAX_FILE_SIZE,
        "allowed_file_types": settings.ALLOWED_FILE_TYPES,
        "upload_dir": settings.UPLOAD_DIR,
        "backup_enabled": settings.BACKUP_ENABLED,
        "audit_enabled": settings.AUDIT_LOG_ENABLED,
        "rate_limit_requests": settings.RATE_LIMIT_REQUESTS,
        "rate_limit_window": settings.RATE_LIMIT_WINDOW
    }


def get_database_config() -> Dict[str, Any]:
    """Get database-specific configuration"""
    return {
        "url": settings.DATABASE_URL,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "echo": settings.DEBUG
    }


def get_redis_config() -> Dict[str, Any]:
    """Get Redis-specific configuration"""
    return {
        "url": settings.REDIS_URL,
        "max_connections": settings.REDIS_MAX_CONNECTIONS,
        "decode_responses": True
    }


def get_monitoring_config() -> Dict[str, Any]:
    """Get monitoring-specific configuration"""
    return {
        "enabled": settings.ENABLE_MONITORING,
        "prometheus_port": settings.PROMETHEUS_PORT,
        "grafana_port": settings.GRAFANA_PORT,
        "log_level": settings.LOG_LEVEL
    }


def get_security_config() -> Dict[str, Any]:
    """Get security-specific configuration"""
    return {
        "secret_key": settings.SECRET_KEY,
        "algorithm": settings.ALGORITHM,
        "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "allowed_origins": settings.ALLOWED_ORIGINS,
        "allowed_methods": settings.ALLOWED_METHODS,
        "allowed_headers": settings.ALLOWED_HEADERS,
        "rate_limit_requests": settings.RATE_LIMIT_REQUESTS,
        "rate_limit_window": settings.RATE_LIMIT_WINDOW
    }


def get_email_config() -> Dict[str, Any]:
    """Get email-specific configuration"""
    return {
        "smtp_host": settings.SMTP_HOST,
        "smtp_port": settings.SMTP_PORT,
        "smtp_username": settings.SMTP_USERNAME,
        "smtp_password": settings.SMTP_PASSWORD,
        "smtp_use_tls": settings.SMTP_USE_TLS
    }


def validate_settings() -> List[str]:
    """Validate settings and return list of issues"""
    issues = []
    
    # Check required settings
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-here":
        issues.append("SECRET_KEY must be set to a secure value")
    
    if not settings.OPENAI_API_KEY:
        issues.append("OPENAI_API_KEY must be set for AI functionality")
    
    if not settings.DATABASE_URL or "localhost" in settings.DATABASE_URL:
        issues.append("DATABASE_URL should point to a production database")
    
    # Check file paths
    if not os.path.exists(settings.UPLOAD_DIR):
        try:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create upload directory: {e}")
    
    if not os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
        try:
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create ChromaDB directory: {e}")
    
    return issues


def get_environment_info() -> Dict[str, Any]:
    """Get environment information for debugging"""
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "log_level": settings.LOG_LEVEL,
        "host": settings.HOST,
        "port": settings.PORT,
        "database_url": settings.DATABASE_URL.replace(settings.DATABASE_URL.split("@")[0].split(":")[-1], "***") if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
        "redis_url": settings.REDIS_URL.replace("redis://", "redis://***@") if "redis://" in settings.REDIS_URL else settings.REDIS_URL,
        "openai_model": settings.OPENAI_MODEL,
        "monitoring_enabled": settings.ENABLE_MONITORING,
        "websockets_enabled": settings.ENABLE_WEBSOCKETS,
        "audit_enabled": settings.AUDIT_LOG_ENABLED,
        "backup_enabled": settings.BACKUP_ENABLED
    }