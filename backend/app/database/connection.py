import os
import logging
from typing import Generator, Optional
from sqlalchemy import create_engine, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import asyncio

from ..core.config import settings

logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

# Database engine
engine = None
SessionLocal = None


def create_database_engine() -> None:
    """Create and configure the database engine"""
    global engine, SessionLocal
    
    try:
        # Parse database URL
        database_url = settings.DATABASE_URL
        
        # Create engine with connection pooling
        engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,  # Enable connection health checks
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=settings.DEBUG,  # Log SQL queries in debug mode
            future=True          # Use SQLAlchemy 2.0 style
        )
        
        # Create session factory
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        logger.info("Database engine created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    if SessionLocal is None:
        create_database_engine()
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def init_database() -> None:
    """Initialize database tables"""
    try:
        if engine is None:
            create_database_engine()
        
        # Import all models to ensure they are registered
        from .models import (
            User, Role, UserRole, Document, Tag, ComplianceFramework,
            ProcessingHistory, AgentExecution, DocumentComparison,
            AuditEvent, SystemMetric, WorkflowTemplate, KnowledgeBase,
            Notification, APILog, SystemConfig
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
        
        # Initialize default data
        await initialize_default_data()
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def initialize_default_data() -> None:
    """Initialize default data in the database"""
    try:
        db = SessionLocal()
        
        # Check if default data already exists
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_admin:
            logger.info("Default data already exists, skipping initialization")
            return
        
        # Create default roles
        admin_role = Role(
            name="admin",
            description="Administrator with full access",
            permissions=["*"]
        )
        
        user_role = Role(
            name="user",
            description="Standard user with basic access",
            permissions=[
                "documents:read",
                "documents:upload",
                "documents:delete",
                "qa:ask",
                "compare:compare",
                "analytics:view"
            ]
        )
        
        analyst_role = Role(
            name="analyst",
            description="Analyst with advanced access",
            permissions=[
                "documents:read",
                "documents:upload",
                "documents:delete",
                "qa:ask",
                "compare:compare",
                "analytics:view",
                "analytics:export",
                "audit:view"
            ]
        )
        
        db.add_all([admin_role, user_role, analyst_role])
        db.commit()
        
        # Create default admin user
        from ..core.security import security_manager
        
        admin_user = User(
            email="admin@example.com",
            full_name="System Administrator",
            hashed_password=security_manager.get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin_user)
        db.commit()
        
        # Assign admin role to admin user
        admin_user_role = UserRole(
            user_id=admin_user.id,
            role_id=admin_role.id,
            assigned_by=admin_user.id
        )
        
        db.add(admin_user_role)
        db.commit()
        
        # Create default compliance frameworks
        frameworks = [
            ComplianceFramework(
                name="GDPR",
                description="General Data Protection Regulation",
                version="2018",
                requirements=["data_minimization", "consent", "right_to_erasure"]
            ),
            ComplianceFramework(
                name="HIPAA",
                description="Health Insurance Portability and Accountability Act",
                version="1996",
                requirements=["privacy_rule", "security_rule", "breach_notification"]
            ),
            ComplianceFramework(
                name="SOX",
                description="Sarbanes-Oxley Act",
                version="2002",
                requirements=["financial_reporting", "internal_controls", "audit_requirements"]
            )
        ]
        
        db.add_all(frameworks)
        db.commit()
        
        # Create default tags
        tags = [
            Tag(name="confidential", description="Confidential documents"),
            Tag(name="public", description="Public documents"),
            Tag(name="financial", description="Financial documents"),
            Tag(name="legal", description="Legal documents"),
            Tag(name="hr", description="Human resources documents"),
            Tag(name="technical", description="Technical documents")
        ]
        
        db.add_all(tags)
        db.commit()
        
        # Create default system configurations
        configs = [
            SystemConfig(
                key="max_file_size_mb",
                value="100",
                description="Maximum file size in MB",
                category="upload"
            ),
            SystemConfig(
                key="allowed_file_types",
                value="pdf,docx,txt,csv,xlsx",
                description="Allowed file types",
                category="upload"
            ),
            SystemConfig(
                key="session_timeout_minutes",
                value="30",
                description="Session timeout in minutes",
                category="security"
            ),
            SystemConfig(
                key="audit_log_retention_days",
                value="90",
                description="Audit log retention period in days",
                category="audit"
            ),
            SystemConfig(
                key="backup_enabled",
                value="true",
                description="Enable automatic backups",
                category="backup"
            ),
            SystemConfig(
                key="monitoring_enabled",
                value="true",
                description="Enable system monitoring",
                category="monitoring"
            )
        ]
        
        db.add_all(configs)
        db.commit()
        
        logger.info("Default data initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize default data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        if engine is None:
            create_database_engine()
        
        # Test connection with a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("Database connection check successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def get_database_info() -> dict:
    """Get database information and statistics"""
    try:
        if engine is None:
            create_database_engine()
        
        db = SessionLocal()
        
        # Get table counts
        table_counts = {}
        tables = [
            "users", "roles", "user_roles", "documents", "tags",
            "compliance_frameworks", "processing_history", "agent_executions",
            "document_comparisons", "audit_events", "system_metrics",
            "workflow_templates", "knowledge_base", "notifications",
            "api_logs", "system_configs"
        ]
        
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                table_counts[table] = count
            except Exception as e:
                logger.warning(f"Could not get count for table {table}: {e}")
                table_counts[table] = 0
        
        # Get database size
        try:
            result = db.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """))
            db_size = result.scalar()
        except Exception:
            db_size = "unknown"
        
        # Get connection info
        pool_info = {
            "pool_size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow()
        }
        
        return {
            "status": "connected",
            "database_url": settings.DATABASE_URL.replace(
                settings.DATABASE_URL.split("@")[0].split(":")[-1], "***"
            ) if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
            "table_counts": table_counts,
            "database_size": db_size,
            "pool_info": pool_info,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }
    finally:
        if 'db' in locals():
            db.close()


async def cleanup_database() -> None:
    """Cleanup database connections"""
    try:
        if engine:
            engine.dispose()
            logger.info("Database engine disposed")
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")


def get_database_session() -> Session:
    """Get a database session (for use outside of FastAPI dependencies)"""
    if SessionLocal is None:
        create_database_engine()
    return SessionLocal()


# Database event listeners for logging
@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    logger.debug("Database connection established")


@event.listens_for(engine, "disconnect")
def receive_disconnect(dbapi_connection, connection_record):
    logger.debug("Database connection closed")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    logger.debug("Database connection checked out")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    logger.debug("Database connection checked in")


# Database health check function
async def health_check_database() -> dict:
    """Perform a comprehensive database health check"""
    try:
        # Check connection
        connection_ok = await check_database_connection()
        if not connection_ok:
            return {
                "status": "unhealthy",
                "error": "Database connection failed",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        
        # Get database info
        db_info = await get_database_info()
        
        # Check for critical issues
        issues = []
        
        # Check if admin user exists
        if db_info.get("table_counts", {}).get("users", 0) == 0:
            issues.append("No users found in database")
        
        # Check if roles exist
        if db_info.get("table_counts", {}).get("roles", 0) == 0:
            issues.append("No roles found in database")
        
        # Check connection pool health
        pool_info = db_info.get("pool_info", {})
        if pool_info.get("checked_out", 0) > pool_info.get("pool_size", 0) * 0.8:
            issues.append("High connection pool usage")
        
        status = "healthy" if not issues else "degraded"
        
        return {
            "status": status,
            "issues": issues,
            "database_info": db_info,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }