import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float, 
    ForeignKey, Table, MetaData, JSON, LargeBinary, Index,
    UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .connection import Base


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    documents = relationship("Document", back_populates="user")
    audit_events = relationship("AuditEvent", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_active', 'is_active'),
        Index('idx_users_created_at', 'created_at'),
    )


class Role(Base):
    """Role model for role-based access control"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, default=list)  # List of permission strings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role")
    
    # Indexes
    __table_args__ = (
        Index('idx_roles_name', 'name'),
        Index('idx_roles_created_at', 'created_at'),
    )


class UserRole(Base):
    """User-Role association model for additional metadata"""
    __tablename__ = "user_roles"
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role", foreign_keys=[role_id], back_populates="user_roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_user_roles_user_id', 'user_id'),
        Index('idx_user_roles_role_id', 'role_id'),
        Index('idx_user_roles_assigned_at', 'assigned_at'),
    )


class Document(Base):
    """Document model for storing document information"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Content and processing
    extracted_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    entities = Column(JSON, nullable=True)  # Extracted entities
    metadata = Column(JSON, nullable=True)  # Document metadata
    
    # Status and processing
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    processing_progress = Column(Float, default=0.0)
    processing_error = Column(Text, nullable=True)
    
    # User and timestamps
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="documents")
    tags = relationship("DocumentTag", back_populates="document")
    processing_history = relationship("ProcessingHistory", back_populates="document")
    agent_executions = relationship("AgentExecution", back_populates="document")
    
    # Indexes
    __table_args__ = (
        Index('idx_documents_uuid', 'uuid'),
        Index('idx_documents_user_id', 'user_id'),
        Index('idx_documents_status', 'status'),
        Index('idx_documents_uploaded_at', 'uploaded_at'),
        Index('idx_documents_file_type', 'file_type'),
    )


class Tag(Base):
    """Tag model for document categorization"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#2196F3")  # Hex color code
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document_tags = relationship("DocumentTag", back_populates="tag")
    
    # Indexes
    __table_args__ = (
        Index('idx_tags_name', 'name'),
        Index('idx_tags_created_at', 'created_at'),
    )


class DocumentTag(Base):
    """Document-Tag association table"""
    __tablename__ = "document_tags"
    
    document_id = Column(Integer, ForeignKey('documents.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="tags")
    tag = relationship("Tag", back_populates="document_tags")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_document_tags_document_id', 'document_id'),
        Index('idx_document_tags_tag_id', 'tag_id'),
    )


class ComplianceFramework(Base):
    """Compliance framework model"""
    __tablename__ = "compliance_frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=True)
    requirements = Column(JSON, nullable=True)  # List of requirements
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_compliance_frameworks_name', 'name'),
        Index('idx_compliance_frameworks_created_at', 'created_at'),
    )


class ProcessingHistory(Base):
    """Processing history model for tracking document processing"""
    __tablename__ = "processing_history"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    stage = Column(String(100), nullable=False)  # ingestion, classification, extraction, etc.
    status = Column(String(50), nullable=False)  # started, completed, failed
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Float, nullable=True)  # Duration in seconds
    result = Column(JSON, nullable=True)  # Processing result
    error_message = Column(Text, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="processing_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_processing_history_document_id', 'document_id'),
        Index('idx_processing_history_stage', 'stage'),
        Index('idx_processing_history_status', 'status'),
        Index('idx_processing_history_start_time', 'start_time'),
    )


class AgentExecution(Base):
    """Agent execution model for tracking AI agent runs"""
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)
    agent_type = Column(String(100), nullable=False)  # orchestrator, classifier, entity, etc.
    execution_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Execution details
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Timing and status
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Float, nullable=True)  # Duration in seconds
    status = Column(String(50), default="running")  # running, completed, failed, timeout
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    document = relationship("Document", back_populates="agent_executions")
    
    # Indexes
    __table_args__ = (
        Index('idx_agent_executions_execution_id', 'execution_id'),
        Index('idx_agent_executions_document_id', 'document_id'),
        Index('idx_agent_executions_agent_type', 'agent_type'),
        Index('idx_agent_executions_status', 'status'),
        Index('idx_agent_executions_start_time', 'start_time'),
    )


class DocumentComparison(Base):
    """Document comparison model for storing comparison results"""
    __tablename__ = "document_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    comparison_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Documents being compared
    document1_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    document2_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    
    # Comparison results
    similarity_score = Column(Float, nullable=True)
    differences = Column(JSON, nullable=True)  # Detailed differences
    summary = Column(Text, nullable=True)
    
    # Metadata
    comparison_type = Column(String(50), default="content")  # content, structure, metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    document1 = relationship("Document", foreign_keys=[document1_id])
    document2 = relationship("Document", foreign_keys=[document2_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_document_comparisons_comparison_id', 'comparison_id'),
        Index('idx_document_comparisons_document1_id', 'document1_id'),
        Index('idx_document_comparisons_document2_id', 'document2_id'),
        Index('idx_document_comparisons_created_at', 'created_at'),
    )


class AuditEvent(Base):
    """Audit event model for security and compliance logging"""
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Event details
    event_type = Column(String(100), nullable=False)  # login, logout, document_upload, etc.
    event_category = Column(String(50), nullable=False)  # authentication, document, system, etc.
    severity = Column(String(20), default="info")  # info, warning, error, critical
    
    # User and session
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    
    # Event data
    details = Column(JSON, nullable=True)  # Additional event details
    resource_type = Column(String(100), nullable=True)  # document, user, system, etc.
    resource_id = Column(String(255), nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_events")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_events_event_id', 'event_id'),
        Index('idx_audit_events_user_id', 'user_id'),
        Index('idx_audit_events_event_type', 'event_type'),
        Index('idx_audit_events_event_category', 'event_category'),
        Index('idx_audit_events_severity', 'severity'),
        Index('idx_audit_events_timestamp', 'timestamp'),
        Index('idx_audit_events_ip_address', 'ip_address'),
    )


class SystemMetric(Base):
    """System metrics model for monitoring"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)  # seconds, bytes, percent, etc.
    
    # Context
    tags = Column(JSON, nullable=True)  # Key-value pairs for filtering
    source = Column(String(100), nullable=True)  # system, application, agent, etc.
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_system_metrics_metric_name', 'metric_name'),
        Index('idx_system_metrics_timestamp', 'timestamp'),
        Index('idx_system_metrics_source', 'source'),
    )


class WorkflowTemplate(Base):
    """Workflow template model for defining processing workflows"""
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0")
    
    # Workflow definition
    stages = Column(JSON, nullable=False)  # List of workflow stages
    conditions = Column(JSON, nullable=True)  # Conditional logic
    settings = Column(JSON, nullable=True)  # Workflow settings
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_workflow_templates_name', 'name'),
        Index('idx_workflow_templates_is_active', 'is_active'),
        Index('idx_workflow_templates_created_at', 'created_at'),
    )


class KnowledgeBase(Base):
    """Knowledge base model for storing AI knowledge"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, qa, rule, etc.
    
    # Categorization
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Metadata
    source = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_knowledge_base_entry_id', 'entry_id'),
        Index('idx_knowledge_base_title', 'title'),
        Index('idx_knowledge_base_category', 'category'),
        Index('idx_knowledge_base_content_type', 'content_type'),
        Index('idx_knowledge_base_is_active', 'is_active'),
        Index('idx_knowledge_base_created_at', 'created_at'),
    )


class Notification(Base):
    """Notification model for user notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Recipient
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Notification details
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="info")  # info, warning, error, success
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    data = Column(JSON, nullable=True)  # Additional notification data
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    # Indexes
    __table_args__ = (
        Index('idx_notifications_notification_id', 'notification_id'),
        Index('idx_notifications_user_id', 'user_id'),
        Index('idx_notifications_is_read', 'is_read'),
        Index('idx_notifications_notification_type', 'notification_type'),
        Index('idx_notifications_priority', 'priority'),
        Index('idx_notifications_created_at', 'created_at'),
    )


class APILog(Base):
    """API log model for tracking API usage"""
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Request details
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE, etc.
    endpoint = Column(String(500), nullable=False)
    status_code = Column(Integer, nullable=False)
    
    # User and session
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Performance
    response_time = Column(Float, nullable=True)  # Response time in seconds
    request_size = Column(Integer, nullable=True)  # Request size in bytes
    response_size = Column(Integer, nullable=True)  # Response size in bytes
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_api_logs_log_id', 'log_id'),
        Index('idx_api_logs_user_id', 'user_id'),
        Index('idx_api_logs_method', 'method'),
        Index('idx_api_logs_endpoint', 'endpoint'),
        Index('idx_api_logs_status_code', 'status_code'),
        Index('idx_api_logs_timestamp', 'timestamp'),
        Index('idx_api_logs_ip_address', 'ip_address'),
    )


class SystemConfig(Base):
    """System configuration model"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # security, performance, monitoring, etc.
    
    # Metadata
    is_encrypted = Column(Boolean, default=False)
    is_sensitive = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_system_configs_key', 'key'),
        Index('idx_system_configs_category', 'category'),
        Index('idx_system_configs_created_at', 'created_at'),
    )
