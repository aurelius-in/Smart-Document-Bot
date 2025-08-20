"""
Celery Configuration for AI Document Agent
Handles distributed task processing for document analysis and AI operations
"""

import os
from celery import Celery
from celery.schedules import crontab
from .config import settings

# Create Celery instance
celery_app = Celery(
    "ai_document_agent",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.document_tasks",
        "app.tasks.agent_tasks", 
        "app.tasks.analytics_tasks",
        "app.tasks.maintenance_tasks"
    ]
)

# Celery Configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.tasks.document_tasks.*": {"queue": "documents"},
        "app.tasks.agent_tasks.*": {"queue": "agents"},
        "app.tasks.analytics_tasks.*": {"queue": "analytics"},
        "app.tasks.maintenance_tasks.*": {"queue": "maintenance"},
    },
    
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    worker_send_task_events=True,
    
    # Result backend
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-expired-documents": {
            "task": "app.tasks.maintenance_tasks.cleanup_expired_documents",
            "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
        },
        "generate-analytics-reports": {
            "task": "app.tasks.analytics_tasks.generate_daily_reports",
            "schedule": crontab(hour=6, minute=0),  # Daily at 6 AM
        },
        "backup-database": {
            "task": "app.tasks.maintenance_tasks.backup_database",
            "schedule": crontab(hour=1, minute=0),  # Daily at 1 AM
        },
        "cleanup-audit-logs": {
            "task": "app.tasks.maintenance_tasks.cleanup_audit_logs",
            "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM
        },
        "update-system-metrics": {
            "task": "app.tasks.analytics_tasks.update_system_metrics",
            "schedule": 300.0,  # Every 5 minutes
        },
        "process-pending-documents": {
            "task": "app.tasks.document_tasks.process_pending_documents",
            "schedule": 60.0,  # Every minute
        },
    },
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_remote_tracebacks=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Security
    security_key=settings.SECRET_KEY,
    security_certificate=None,
    security_cert_store=None,
)

# Task annotations for specific task configurations
celery_app.conf.task_annotations = {
    "app.tasks.document_tasks.process_document": {
        "rate_limit": "10/m",  # 10 tasks per minute
        "time_limit": 600,  # 10 minutes
        "soft_time_limit": 300,  # 5 minutes
    },
    "app.tasks.agent_tasks.execute_agent": {
        "rate_limit": "5/m",  # 5 tasks per minute
        "time_limit": 900,  # 15 minutes
        "soft_time_limit": 600,  # 10 minutes
    },
    "app.tasks.analytics_tasks.generate_report": {
        "rate_limit": "1/h",  # 1 task per hour
        "time_limit": 1800,  # 30 minutes
        "soft_time_limit": 1200,  # 20 minutes
    },
}

# Error handling
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f"Request: {self.request!r}")

# Health check task
@celery_app.task
def health_check():
    """Health check task for monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": settings.APP_VERSION
    }

# Task failure handling
@celery_app.task(bind=True, max_retries=3)
def handle_task_failure(self, task_id, exc, traceback):
    """Handle task failures with retry logic"""
    try:
        # Log the failure
        print(f"Task {task_id} failed: {exc}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries  # Exponential backoff
            raise self.retry(countdown=countdown, exc=exc)
        else:
            # Max retries reached, mark as permanently failed
            print(f"Task {task_id} permanently failed after {self.max_retries} retries")
            
    except Exception as e:
        print(f"Error handling task failure: {e}")

# Task success handling
@celery_app.task
def handle_task_success(task_id, result):
    """Handle successful task completion"""
    try:
        print(f"Task {task_id} completed successfully: {result}")
        # Additional success handling logic here
    except Exception as e:
        print(f"Error handling task success: {e}")

# Celery signal handlers
from celery.signals import task_success, task_failure, task_revoked

@task_success.connect
def task_success_handler(sender=None, **kwargs):
    """Handle task success events"""
    task_id = kwargs.get("result", {}).get("id")
    if task_id:
        handle_task_success.delay(task_id, kwargs.get("result"))

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwargs):
    """Handle task failure events"""
    if task_id:
        handle_task_failure.delay(task_id, str(exception), traceback)

@task_revoked.connect
def task_revoked_handler(sender=None, request=None, terminated=None, signum=None, expired=None, **kwargs):
    """Handle task revocation events"""
    task_id = request.id if request else None
    if task_id:
        print(f"Task {task_id} was revoked (terminated={terminated}, expired={expired})")

# Export the Celery app
__all__ = ["celery_app"]
