"""
Celery Tasks Package for AI Document Agent
Handles distributed task processing for document analysis and AI operations
"""

from .document_tasks import *
from .agent_tasks import *
from .analytics_tasks import *
from .maintenance_tasks import *

__all__ = [
    # Document tasks
    "process_document",
    "extract_text",
    "classify_document",
    "extract_entities",
    "assess_risk",
    "compare_documents",
    
    # Agent tasks
    "execute_agent",
    "orchestrate_workflow",
    "run_qa_agent",
    "run_summarizer_agent",
    "run_translator_agent",
    "run_sentiment_agent",
    
    # Analytics tasks
    "generate_daily_reports",
    "update_system_metrics",
    "analyze_performance",
    "generate_insights",
    
    # Maintenance tasks
    "cleanup_expired_documents",
    "backup_database",
    "cleanup_audit_logs",
    "optimize_database",
    "health_check",
]
