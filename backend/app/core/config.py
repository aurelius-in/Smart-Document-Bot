import os
from typing import List, Optional
from pydantic import BaseSettings, Field
from pydantic.validator import validator


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
    
    # Compliance settings
    COMPLIANCE_FRAMEWORKS: List[str] = Field(
        default=["GDPR", "SOX", "HIPAA", "ISO27001"],
        env="COMPLIANCE_FRAMEWORKS"
    )
    COMPLIANCE_SCAN_ENABLED: bool = Field(default=True, env="COMPLIANCE_SCAN_ENABLED")
    
    # Performance settings
    ENABLE_CACHING: bool = Field(default=True, env="ENABLE_CACHING")
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    ENABLE_RATE_LIMITING: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # Notification settings
    ENABLE_NOTIFICATIONS: bool = Field(default=False, env="ENABLE_NOTIFICATIONS")
    SMTP_HOST: str = Field(default="", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(default="", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    
    # External services
    ENABLE_OCR: bool = Field(default=True, env="ENABLE_OCR")
    OCR_SERVICE_URL: str = Field(default="", env="OCR_SERVICE_URL")
    ENABLE_TRANSLATION: bool = Field(default=False, env="ENABLE_TRANSLATION")
    TRANSLATION_SERVICE_URL: str = Field(default="", env="TRANSLATION_SERVICE_URL")
    
    # Development settings
    ENABLE_SWAGGER: bool = Field(default=True, env="ENABLE_SWAGGER")
    ENABLE_RELOAD: bool = Field(default=True, env="ENABLE_RELOAD")
    ENABLE_DEBUG_TOOLBAR: bool = Field(default=False, env="ENABLE_DEBUG_TOOLBAR")
    
    # Testing settings
    TESTING: bool = Field(default=False, env="TESTING")
    TEST_DATABASE_URL: str = Field(default="sqlite:///./test.db", env="TEST_DATABASE_URL")
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(",")]
        return v
    
    @validator("COMPLIANCE_FRAMEWORKS", pre=True)
    def parse_compliance_frameworks(cls, v):
        if isinstance(v, str):
            return [framework.strip() for framework in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class AgentConfig:
    """Agent-specific configuration"""
    
    # Ingestion Agent
    INGESTION_OCR_ENABLED: bool = True
    INGESTION_PDF_EXTRACTION_ENABLED: bool = True
    INGESTION_TEXT_NORMALIZATION_ENABLED: bool = True
    INGESTION_MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Classifier Agent
    CLASSIFIER_CONFIDENCE_THRESHOLD: float = 0.7
    CLASSIFIER_MAX_CLASSES: int = 10
    CLASSIFIER_ENABLE_CONTENT_ANALYSIS: bool = True
    
    # Entity Agent
    ENTITY_NER_ENABLED: bool = True
    ENTITY_CLAUSE_EXTRACTION_ENABLED: bool = True
    ENTITY_KEY_INFO_EXTRACTION_ENABLED: bool = True
    ENTITY_MAX_ENTITIES: int = 100
    
    # Risk Agent
    RISK_COMPLIANCE_ANALYSIS_ENABLED: bool = True
    RISK_FINANCIAL_ANALYSIS_ENABLED: bool = True
    RISK_OPERATIONAL_ANALYSIS_ENABLED: bool = True
    RISK_SCORING_ENABLED: bool = True
    RISK_THRESHOLD_HIGH: float = 0.8
    RISK_THRESHOLD_MEDIUM: float = 0.5
    
    # QA Agent
    QA_FACTUAL_QUESTIONS_ENABLED: bool = True
    QA_COMPLIANCE_QUESTIONS_ENABLED: bool = True
    QA_RISK_QUESTIONS_ENABLED: bool = True
    QA_ACTION_QUESTIONS_ENABLED: bool = True
    QA_MAX_QUESTIONS: int = 20
    
    # Compare Agent
    COMPARE_SEMANTIC_ENABLED: bool = True
    COMPARE_STRUCTURAL_ENABLED: bool = True
    COMPARE_COMPLIANCE_ENABLED: bool = True
    COMPARE_ENTITY_ENABLED: bool = True
    COMPARE_SIMILARITY_THRESHOLD: float = 0.8
    
    # Audit Agent
    AUDIT_TRAIL_GENERATION_ENABLED: bool = True
    AUDIT_COMPLIANCE_REPORTING_ENABLED: bool = True
    AUDIT_BUNDLE_GENERATION_ENABLED: bool = True
    AUDIT_VALIDATION_ENABLED: bool = True
    AUDIT_RETENTION_DAYS: int = 90


class WorkflowConfig:
    """Workflow-specific configuration"""
    
    # Planning
    PLANNING_ENABLED: bool = True
    PLANNING_MAX_STAGES: int = 10
    PLANNING_PARALLEL_EXECUTION: bool = True
    
    # Execution
    EXECUTION_TIMEOUT: int = 300  # 5 minutes
    EXECUTION_MAX_RETRIES: int = 3
    EXECUTION_RETRY_DELAY: int = 5  # seconds
    
    # Monitoring
    MONITORING_ENABLED: bool = True
    MONITORING_INTERVAL: int = 5  # seconds
    MONITORING_METRICS_ENABLED: bool = True
    
    # Error handling
    ERROR_HANDLING_ENABLED: bool = True
    ERROR_RETRY_ENABLED: bool = True
    ERROR_FALLBACK_ENABLED: bool = True


class SecurityConfig:
    """Security-specific configuration"""
    
    # Authentication
    AUTH_ENABLED: bool = True
    AUTH_JWT_ENABLED: bool = True
    AUTH_OAUTH_ENABLED: bool = False
    AUTH_SESSION_TIMEOUT: int = 3600  # 1 hour
    
    # Authorization
    AUTHORIZATION_ENABLED: bool = True
    AUTHORIZATION_RBAC_ENABLED: bool = True
    AUTHORIZATION_PERMISSIONS_ENABLED: bool = True
    
    # Encryption
    ENCRYPTION_ENABLED: bool = False
    ENCRYPTION_ALGORITHM: str = "AES-256"
    ENCRYPTION_KEY_ROTATION_ENABLED: bool = False
    
    # Audit
    AUDIT_SECURITY_ENABLED: bool = True
    AUDIT_ACCESS_LOGGING_ENABLED: bool = True
    AUDIT_CHANGE_LOGGING_ENABLED: bool = True


class PerformanceConfig:
    """Performance-specific configuration"""
    
    # Caching
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 1000
    CACHE_REDIS_ENABLED: bool = True
    
    # Rate limiting
    RATE_LIMITING_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    RATE_LIMIT_BURST: int = 10
    
    # Connection pooling
    CONNECTION_POOLING_ENABLED: bool = True
    CONNECTION_POOL_SIZE: int = 10
    CONNECTION_POOL_MAX_OVERFLOW: int = 20
    
    # Async processing
    ASYNC_PROCESSING_ENABLED: bool = True
    ASYNC_WORKER_COUNT: int = 4
    ASYNC_QUEUE_SIZE: int = 100


# Create settings instance
settings = Settings()

# Create configuration instances
agent_config = AgentConfig()
workflow_config = WorkflowConfig()
security_config = SecurityConfig()
performance_config = PerformanceConfig()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def get_agent_config() -> AgentConfig:
    """Get agent configuration"""
    return agent_config


def get_workflow_config() -> WorkflowConfig:
    """Get workflow configuration"""
    return workflow_config


def get_security_config() -> SecurityConfig:
    """Get security configuration"""
    return security_config


def get_performance_config() -> PerformanceConfig:
    """Get performance configuration"""
    return performance_config


def validate_configuration():
    """Validate configuration settings"""
    errors = []
    
    # Validate required settings
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-here":
        errors.append("SECRET_KEY must be set to a secure value")
    
    if not settings.LLM_API_KEY:
        errors.append("OPENAI_API_KEY must be set for LLM functionality")
    
    # Validate file paths
    if not os.path.exists(settings.UPLOAD_DIR):
        try:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        except Exception as e:
            errors.append(f"Failed to create upload directory: {e}")
    
    if not os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
        try:
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        except Exception as e:
            errors.append(f"Failed to create ChromaDB directory: {e}")
    
    # Validate numeric ranges
    if settings.AGENT_CONFIDENCE_THRESHOLD < 0 or settings.AGENT_CONFIDENCE_THRESHOLD > 1:
        errors.append("AGENT_CONFIDENCE_THRESHOLD must be between 0 and 1")
    
    if settings.WORKFLOW_MAX_STAGES < 1 or settings.WORKFLOW_MAX_STAGES > 50:
        errors.append("WORKFLOW_MAX_STAGES must be between 1 and 50")
    
    if settings.MAX_FILE_SIZE < 1024 or settings.MAX_FILE_SIZE > 100 * 1024 * 1024:
        errors.append("MAX_FILE_SIZE must be between 1KB and 100MB")
    
    # Validate URLs
    if settings.DATABASE_URL and not settings.DATABASE_URL.startswith(("sqlite://", "postgresql://", "mysql://")):
        errors.append("DATABASE_URL must be a valid database URL")
    
    if settings.REDIS_URL and not settings.REDIS_URL.startswith("redis://"):
        errors.append("REDIS_URL must be a valid Redis URL")
    
    return errors


def get_environment_info():
    """Get environment information"""
    return {
        "environment": "development" if settings.DEBUG else "production",
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "host": settings.HOST,
        "port": settings.PORT,
        "llm_model": settings.LLM_MODEL,
        "database": settings.DATABASE_URL.split("://")[0] if "://" in settings.DATABASE_URL else "sqlite",
        "redis_enabled": bool(settings.REDIS_URL),
        "monitoring_enabled": settings.ENABLE_MONITORING,
        "audit_enabled": settings.AUDIT_ENABLED,
        "caching_enabled": settings.ENABLE_CACHING,
        "rate_limiting_enabled": settings.ENABLE_RATE_LIMITING
    }
