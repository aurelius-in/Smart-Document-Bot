from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any

Base = declarative_base()

# Association tables for many-to-many relationships
document_tags = Table(
    'document_tags',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

document_compliance_frameworks = Table(
    'document_compliance_frameworks',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),
    Column('framework_id', Integer, ForeignKey('compliance_frameworks.id'), primary_key=True)
)

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    documents = relationship("Document", back_populates="uploaded_by_user")
    audit_events = relationship("AuditEvent", back_populates="user")
    processing_history = relationship("ProcessingHistory", back_populates="user")
    user_roles = relationship("Role", secondary=user_roles, back_populates="users")


class Role(Base):
    """Role model for role-based access control"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=True)  # Store permissions as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="user_roles")


class Document(Base):
    """Document model for storing document information"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)  # Extracted text content
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    doc_type = Column(String(50), nullable=True)  # CONTRACT, INVOICE, etc.
    domain = Column(String(100), nullable=True)  # LEGAL, FINANCIAL, etc.
    
    # Processing metadata
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_result = Column(JSON, nullable=True)  # Store agent processing results
    confidence_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional metadata
    tags = Column(JSON, nullable=True)  # Document tags
    entities = Column(JSON, nullable=True)  # Extracted entities
    clauses = Column(JSON, nullable=True)  # Extracted clauses
    risks = Column(JSON, nullable=True)  # Risk assessment results
    qa_pairs = Column(JSON, nullable=True)  # Generated Q&A pairs
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    uploaded_by_user = relationship("User", back_populates="documents")
    processing_history = relationship("ProcessingHistory", back_populates="document")
    audit_events = relationship("AuditEvent", back_populates="document")
    comparisons = relationship("DocumentComparison", foreign_keys="DocumentComparison.document_a_id")
    comparisons_as_b = relationship("DocumentComparison", foreign_keys="DocumentComparison.document_b_id")
    document_tags = relationship("Tag", secondary=document_tags, back_populates="documents")
    compliance_frameworks = relationship("ComplianceFramework", secondary=document_compliance_frameworks, back_populates="documents")


class Tag(Base):
    """Tag model for document categorization"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    documents = relationship("Document", secondary=document_tags, back_populates="document_tags")


class ComplianceFramework(Base):
    """Compliance framework model"""
    __tablename__ = "compliance_frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # GDPR, SOX, HIPAA, etc.
    description = Column(Text, nullable=True)
    version = Column(String(20), nullable=True)
    requirements = Column(JSON, nullable=True)  # Framework requirements
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    documents = relationship("Document", secondary=document_compliance_frameworks, back_populates="compliance_frameworks")


class ProcessingHistory(Base):
    """Processing history model for tracking document processing"""
    __tablename__ = "processing_history"
    
    id = Column(Integer, primary_key=True, index=True)
    processing_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Processing details
    workflow_id = Column(String(100), nullable=True)
    current_stage = Column(String(100), nullable=True)
    completed_stages = Column(JSON, nullable=True)  # List of completed stages
    failed_stages = Column(JSON, nullable=True)  # List of failed stages
    total_execution_time = Column(Float, nullable=True)  # Total execution time in seconds
    progress_percentage = Column(Float, default=0.0)
    
    # Results
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    result = Column(JSON, nullable=True)  # Processing result
    confidence = Column(Float, nullable=True)
    rationale = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="processing_history")
    user = relationship("User", back_populates="processing_history")
    agent_executions = relationship("AgentExecution", back_populates="processing_history")


class AgentExecution(Base):
    """Agent execution model for tracking individual agent runs"""
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Agent details
    agent_type = Column(String(50), nullable=False)  # classifier, entity, risk, etc.
    agent_name = Column(String(100), nullable=False)
    
    # Execution details
    input_size = Column(Integer, nullable=True)
    output_size = Column(Integer, nullable=True)
    execution_time = Column(Float, nullable=True)  # Execution time in seconds
    memory_usage = Column(Float, nullable=True)  # Memory usage in MB
    cpu_usage = Column(Float, nullable=True)  # CPU usage percentage
    
    # Results
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    confidence = Column(Float, nullable=True)
    output = Column(JSON, nullable=True)  # Agent output
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    processing_history_id = Column(Integer, ForeignKey("processing_history.id"), nullable=False)
    
    # Relationships
    processing_history = relationship("ProcessingHistory", back_populates="agent_executions")


class DocumentComparison(Base):
    """Document comparison model"""
    __tablename__ = "document_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    comparison_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Comparison details
    comparison_type = Column(String(50), nullable=False)  # semantic, structural, compliance, etc.
    similarity_score = Column(Float, nullable=True)
    differences = Column(JSON, nullable=True)  # Detailed differences
    risk_changes = Column(JSON, nullable=True)  # Risk changes between documents
    
    # Results
    status = Column(String(50), default="pending")
    result = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    document_a_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    document_b_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    document_a = relationship("Document", foreign_keys=[document_a_id])
    document_b = relationship("Document", foreign_keys=[document_b_id])
    creator = relationship("User")


class AuditEvent(Base):
    """Audit event model for compliance and security auditing"""
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Event details
    event_type = Column(String(100), nullable=False)  # document_upload, processing_start, etc.
    event_category = Column(String(50), nullable=False)  # security, compliance, system, etc.
    severity = Column(String(20), default="info")  # info, warning, error, critical
    
    # Event data
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Additional event details
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_events")
    document = relationship("Document", back_populates="audit_events")


class SystemMetrics(Base):
    """System metrics model for monitoring and performance tracking"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Metric details
    metric_name = Column(String(100), nullable=False)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, histogram, summary
    value = Column(Float, nullable=False)
    labels = Column(JSON, nullable=True)  # Metric labels
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional metadata
    description = Column(Text, nullable=True)
    unit = Column(String(20), nullable=True)  # seconds, bytes, percentage, etc.


class WorkflowTemplate(Base):
    """Workflow template model for predefined processing workflows"""
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Template details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0.0")
    
    # Workflow configuration
    stages = Column(JSON, nullable=False)  # Workflow stages configuration
    agent_config = Column(JSON, nullable=True)  # Agent-specific configuration
    workflow_config = Column(JSON, nullable=True)  # Workflow-specific configuration
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User")


class KnowledgeBase(Base):
    """Knowledge base model for storing domain knowledge and rules"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    kb_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Knowledge base details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=True)  # legal, financial, healthcare, etc.
    
    # Content
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=False)  # rule, guideline, policy, etc.
    vector_embedding = Column(JSON, nullable=True)  # Vector embedding for similarity search
    
    # Metadata
    source = Column(String(255), nullable=True)
    version = Column(String(20), default="1.0.0")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User")


class Notification(Base):
    """Notification model for system notifications and alerts"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Notification details
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # info, warning, error, success
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # Delivery
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    
    # Relationships
    user = relationship("User")
    document = relationship("Document")


class APILog(Base):
    """API log model for tracking API usage and performance"""
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Request details
    method = Column(String(10), nullable=False)
    endpoint = Column(String(255), nullable=False)
    status_code = Column(Integer, nullable=False)
    
    # Performance
    response_time = Column(Float, nullable=True)  # Response time in seconds
    request_size = Column(Integer, nullable=True)  # Request size in bytes
    response_size = Column(Integer, nullable=True)  # Response size in bytes
    
    # Request data
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_headers = Column(JSON, nullable=True)
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User")


class SystemConfiguration(Base):
    """System configuration model for storing application settings"""
    __tablename__ = "system_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, index=True, nullable=False)
    
    # Configuration details
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), nullable=False)  # string, integer, float, boolean, json
    description = Column(Text, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    updater = relationship("User")
