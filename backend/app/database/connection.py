from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator

from ..core.config import settings

logger = logging.getLogger(__name__)

# Database engine
engine = None
SessionLocal = None
Base = declarative_base()


def create_database_engine():
    """Create database engine based on configuration"""
    global engine, SessionLocal
    
    database_url = settings.DATABASE_URL
    
    # Configure engine based on database type
    if database_url.startswith("sqlite"):
        # SQLite configuration
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.DEBUG
        )
    elif database_url.startswith("postgresql"):
        # PostgreSQL configuration
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=settings.DEBUG
        )
    else:
        # Default configuration
        engine = create_engine(
            database_url,
            echo=settings.DEBUG
        )
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logger.info(f"Database engine created for: {database_url}")
    return engine


def get_database_session() -> Generator[Session, None, None]:
    """Get database session"""
    if SessionLocal is None:
        create_database_engine()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database tables"""
    global engine
    
    if engine is None:
        create_database_engine()
    
    try:
        # Import all models to ensure they are registered
        from .models import (
            User, Role, Document, Tag, ComplianceFramework,
            ProcessingHistory, AgentExecution, DocumentComparison,
            AuditEvent, SystemMetrics, WorkflowTemplate,
            KnowledgeBase, Notification, APILog, SystemConfiguration
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create default data
        create_default_data()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def create_default_data():
    """Create default data in database"""
    try:
        db = next(get_database_session())
        
        # Import models
        from .models import User, Role, ComplianceFramework, Tag
        from ..core.security import get_password_hash
        
        # Create default roles
        default_roles = [
            {"name": "admin", "description": "Administrator with full access"},
            {"name": "manager", "description": "Manager with limited admin access"},
            {"name": "user", "description": "Regular user with basic access"}
        ]
        
        for role_data in default_roles:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
        
        # Create default admin user
        admin_email = "admin@example.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
        
        # Create default compliance frameworks
        default_frameworks = [
            {"name": "GDPR", "description": "General Data Protection Regulation"},
            {"name": "HIPAA", "description": "Health Insurance Portability and Accountability Act"},
            {"name": "SOX", "description": "Sarbanes-Oxley Act"},
            {"name": "PCI-DSS", "description": "Payment Card Industry Data Security Standard"}
        ]
        
        for framework_data in default_frameworks:
            existing_framework = db.query(ComplianceFramework).filter(
                ComplianceFramework.name == framework_data["name"]
            ).first()
            if not existing_framework:
                framework = ComplianceFramework(**framework_data)
                db.add(framework)
        
        # Create default tags
        default_tags = [
            {"name": "contract", "description": "Legal contracts", "color": "#2196F3"},
            {"name": "invoice", "description": "Financial invoices", "color": "#4CAF50"},
            {"name": "policy", "description": "Company policies", "color": "#FF9800"},
            {"name": "report", "description": "Business reports", "color": "#9C27B0"},
            {"name": "compliance", "description": "Compliance documents", "color": "#F44336"}
        ]
        
        for tag_data in default_tags:
            existing_tag = db.query(Tag).filter(Tag.name == tag_data["name"]).first()
            if not existing_tag:
                tag = Tag(**tag_data)
                db.add(tag)
        
        # Commit all changes
        db.commit()
        logger.info("Default data created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create default data: {e}")
        db.rollback()
    finally:
        db.close()


def check_database_connection():
    """Check if database connection is working"""
    try:
        if engine is None:
            create_database_engine()
        
        # Test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        logger.info("Database connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def get_database_info():
    """Get database information"""
    if engine is None:
        return {"status": "not_initialized"}
    
    try:
        with engine.connect() as conn:
            # Get database type
            db_type = engine.dialect.name
            
            # Get database URL (without credentials)
            db_url = str(engine.url).replace(str(engine.url.password), "****") if engine.url.password else str(engine.url)
            
            # Test connection
            conn.execute("SELECT 1")
            
            return {
                "status": "connected",
                "type": db_type,
                "url": db_url,
                "pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else None,
                "checked_out_connections": engine.pool.checkedout() if hasattr(engine.pool, 'checkedout') else None
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def reset_database():
    """Reset database (drop and recreate all tables)"""
    global engine
    
    if engine is None:
        create_database_engine()
    
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("All database tables dropped")
        
        # Recreate all tables
        Base.metadata.create_all(bind=engine)
        logger.info("All database tables recreated")
        
        # Create default data
        create_default_data()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        return False


# Database dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI endpoints"""
    return get_database_session()