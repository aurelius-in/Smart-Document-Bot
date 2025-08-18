from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging
from typing import Generator, Optional
import time
import threading

from ..core.config import get_settings
from .models import Base

settings = get_settings()
logger = logging.getLogger(__name__)

# Database engine configuration
def create_database_engine():
    """Create database engine with appropriate configuration"""
    database_url = settings.DATABASE_URL
    
    # Engine configuration
    engine_kwargs = {
        "echo": settings.DEBUG,  # Log SQL queries in debug mode
        "pool_pre_ping": True,  # Verify connections before use
        "pool_recycle": 3600,  # Recycle connections after 1 hour
        "pool_size": 10,  # Connection pool size
        "max_overflow": 20,  # Maximum overflow connections
    }
    
    # SQLite specific configuration
    if database_url.startswith("sqlite"):
        engine_kwargs.update({
            "connect_args": {
                "check_same_thread": False,
                "timeout": 30
            },
            "poolclass": StaticPool
        })
    
    # PostgreSQL specific configuration
    elif database_url.startswith("postgresql"):
        engine_kwargs.update({
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "pool_size": 10,
            "max_overflow": 20,
            "echo": settings.DEBUG
        })
    
    try:
        engine = create_engine(database_url, **engine_kwargs)
        logger.info(f"Database engine created successfully: {database_url.split('@')[0]}@...")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise

# Create engine instance
engine = create_database_engine()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database event listeners
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance and features"""
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries"""
    context._query_start_time = time.time()

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution time"""
    if hasattr(context, '_query_start_time'):
        total = time.time() - context._query_start_time
        if total > 1.0:  # Log queries taking more than 1 second
            logger.warning(f"Slow query detected ({total:.2f}s): {statement[:100]}...")

# Database dependency
def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Database session context manager
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Database initialization
def init_database():
    """Initialize database tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create indexes for better performance
        create_database_indexes()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def create_database_indexes():
    """Create database indexes for better performance"""
    try:
        with engine.connect() as connection:
            # Create indexes for frequently queried columns
            indexes = [
                # Users table
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)",
                
                # Documents table
                "CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by ON documents(uploaded_by)",
                "CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at ON documents(uploaded_at)",
                "CREATE INDEX IF NOT EXISTS idx_documents_doc_type ON documents(doc_type)",
                "CREATE INDEX IF NOT EXISTS idx_documents_processing_status ON documents(processing_status)",
                "CREATE INDEX IF NOT EXISTS idx_documents_domain ON documents(domain)",
                
                # Processing history table
                "CREATE INDEX IF NOT EXISTS idx_processing_history_processing_id ON processing_history(processing_id)",
                "CREATE INDEX IF NOT EXISTS idx_processing_history_document_id ON processing_history(document_id)",
                "CREATE INDEX IF NOT EXISTS idx_processing_history_user_id ON processing_history(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_processing_history_status ON processing_history(status)",
                "CREATE INDEX IF NOT EXISTS idx_processing_history_started_at ON processing_history(started_at)",
                
                # Agent executions table
                "CREATE INDEX IF NOT EXISTS idx_agent_executions_execution_id ON agent_executions(execution_id)",
                "CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_type ON agent_executions(agent_type)",
                "CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_executions(status)",
                "CREATE INDEX IF NOT EXISTS idx_agent_executions_started_at ON agent_executions(started_at)",
                
                # Document comparisons table
                "CREATE INDEX IF NOT EXISTS idx_document_comparisons_comparison_id ON document_comparisons(comparison_id)",
                "CREATE INDEX IF NOT EXISTS idx_document_comparisons_document_a_id ON document_comparisons(document_a_id)",
                "CREATE INDEX IF NOT EXISTS idx_document_comparisons_document_b_id ON document_comparisons(document_b_id)",
                "CREATE INDEX IF NOT EXISTS idx_document_comparisons_created_by ON document_comparisons(created_by)",
                
                # Audit events table
                "CREATE INDEX IF NOT EXISTS idx_audit_events_event_id ON audit_events(event_id)",
                "CREATE INDEX IF NOT EXISTS idx_audit_events_event_type ON audit_events(event_type)",
                "CREATE INDEX IF NOT EXISTS idx_audit_events_event_category ON audit_events(event_category)",
                "CREATE INDEX IF NOT EXISTS idx_audit_events_severity ON audit_events(severity)",
                "CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp ON audit_events(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_audit_events_user_id ON audit_events(user_id)",
                
                # System metrics table
                "CREATE INDEX IF NOT EXISTS idx_system_metrics_metric_id ON system_metrics(metric_id)",
                "CREATE INDEX IF NOT EXISTS idx_system_metrics_metric_name ON system_metrics(metric_name)",
                "CREATE INDEX IF NOT EXISTS idx_system_metrics_metric_type ON system_metrics(metric_type)",
                "CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)",
                
                # API logs table
                "CREATE INDEX IF NOT EXISTS idx_api_logs_method ON api_logs(method)",
                "CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint)",
                "CREATE INDEX IF NOT EXISTS idx_api_logs_status_code ON api_logs(status_code)",
                "CREATE INDEX IF NOT EXISTS idx_api_logs_timestamp ON api_logs(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_api_logs_user_id ON api_logs(user_id)",
                
                # Notifications table
                "CREATE INDEX IF NOT EXISTS idx_notifications_notification_id ON notifications(notification_id)",
                "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_notifications_notification_type ON notifications(notification_type)",
                "CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority)",
                "CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)",
                "CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)",
            ]
            
            for index_sql in indexes:
                try:
                    connection.execute(index_sql)
                except Exception as e:
                    # Ignore errors for indexes that already exist
                    if "already exists" not in str(e).lower():
                        logger.warning(f"Failed to create index: {e}")
            
            connection.commit()
            logger.info("Database indexes created successfully")
            
    except Exception as e:
        logger.error(f"Failed to create database indexes: {e}")
        raise

# Database health check
def check_database_health() -> dict:
    """Check database health and return status"""
    try:
        with engine.connect() as connection:
            # Test basic connectivity
            connection.execute("SELECT 1")
            
            # Get database statistics
            stats = {}
            
            # Count records in main tables
            tables = [
                "users", "documents", "processing_history", 
                "agent_executions", "audit_events", "system_metrics"
            ]
            
            for table in tables:
                try:
                    result = connection.execute(f"SELECT COUNT(*) FROM {table}")
                    count = result.scalar()
                    stats[f"{table}_count"] = count
                except Exception as e:
                    logger.warning(f"Failed to count records in {table}: {e}")
                    stats[f"{table}_count"] = 0
            
            return {
                "status": "healthy",
                "database_url": settings.DATABASE_URL.split('@')[0] + "@...",
                "statistics": stats
            }
            
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_url": settings.DATABASE_URL.split('@')[0] + "@..."
        }

# Database cleanup
def cleanup_old_data():
    """Clean up old data to prevent database bloat"""
    try:
        with get_db_session() as db:
            # Clean up old audit events (older than 90 days)
            cleanup_sql = """
            DELETE FROM audit_events 
            WHERE timestamp < NOW() - INTERVAL '90 days'
            """
            db.execute(cleanup_sql)
            
            # Clean up old API logs (older than 30 days)
            cleanup_sql = """
            DELETE FROM api_logs 
            WHERE timestamp < NOW() - INTERVAL '30 days'
            """
            db.execute(cleanup_sql)
            
            # Clean up old system metrics (older than 7 days)
            cleanup_sql = """
            DELETE FROM system_metrics 
            WHERE timestamp < NOW() - INTERVAL '7 days'
            """
            db.execute(cleanup_sql)
            
            # Clean up old notifications (older than 30 days)
            cleanup_sql = """
            DELETE FROM notifications 
            WHERE created_at < NOW() - INTERVAL '30 days' AND is_read = true
            """
            db.execute(cleanup_sql)
            
            db.commit()
            logger.info("Database cleanup completed successfully")
            
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")
        raise

# Database backup
def create_database_backup(backup_path: str):
    """Create database backup"""
    try:
        if settings.DATABASE_URL.startswith("sqlite"):
            # SQLite backup
            import shutil
            shutil.copy2(settings.DATABASE_URL.replace("sqlite:///", ""), backup_path)
        elif settings.DATABASE_URL.startswith("postgresql"):
            # PostgreSQL backup using pg_dump
            import subprocess
            import os
            
            # Extract connection details from URL
            url_parts = settings.DATABASE_URL.replace("postgresql://", "").split("/")
            host_port = url_parts[0].split("@")[-1]
            host, port = host_port.split(":") if ":" in host_port else (host_port, "5432")
            user_pass = url_parts[0].split("@")[0]
            user, password = user_pass.split(":") if ":" in user_pass else (user_pass, "")
            database = url_parts[1].split("?")[0]
            
            # Set environment variables for pg_dump
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            
            # Run pg_dump
            cmd = [
                "pg_dump",
                "-h", host,
                "-p", port,
                "-U", user,
                "-d", database,
                "-f", backup_path,
                "--format=custom",
                "--verbose"
            ]
            
            subprocess.run(cmd, env=env, check=True)
        
        logger.info(f"Database backup created successfully: {backup_path}")
        
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        raise

# Database migration utilities
def get_database_version() -> str:
    """Get current database version"""
    try:
        with engine.connect() as connection:
            # Check if version table exists
            result = connection.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='alembic_version'
            """)
            
            if result.fetchone():
                # Get version from alembic_version table
                result = connection.execute("SELECT version_num FROM alembic_version")
                version = result.scalar()
                return version or "unknown"
            else:
                return "no_migrations"
                
    except Exception as e:
        logger.error(f"Failed to get database version: {e}")
        return "unknown"

def upgrade_database():
    """Upgrade database to latest version"""
    try:
        import subprocess
        import sys
        
        # Run alembic upgrade
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Database upgraded successfully")
            return True
        else:
            logger.error(f"Database upgrade failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to upgrade database: {e}")
        return False

# Thread-local storage for database sessions
class DatabaseSessionManager:
    """Thread-local database session manager"""
    
    def __init__(self):
        self._local = threading.local()
    
    def get_session(self) -> Optional[Session]:
        """Get current thread's database session"""
        if not hasattr(self._local, 'session'):
            self._local.session = SessionLocal()
        return self._local.session
    
    def close_session(self):
        """Close current thread's database session"""
        if hasattr(self._local, 'session'):
            self._local.session.close()
            delattr(self._local, 'session')

# Global session manager
session_manager = DatabaseSessionManager()

# Database middleware for FastAPI
class DatabaseMiddleware:
    """Middleware to manage database sessions per request"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Create session for HTTP requests
            session_manager.get_session()
            
            try:
                await self.app(scope, receive, send)
            finally:
                # Close session after request
                session_manager.close_session()
        else:
            await self.app(scope, receive, send)
