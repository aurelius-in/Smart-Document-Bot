from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Types of agents in the system"""
    ORCHESTRATOR = "orchestrator"
    INGESTION = "ingestion"
    CLASSIFIER = "classifier"
    ENTITY = "entity"
    RISK = "risk"
    QA = "qa"
    COMPARE = "compare"
    AUDIT = "audit"


class ConfidenceLevel(str, Enum):
    """Confidence levels for agent outputs"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class SeverityLevel(str, Enum):
    """Risk severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DocumentType(str, Enum):
    """Document types for classification"""
    CONTRACT = "contract"
    INVOICE = "invoice"
    POLICY = "policy"
    REGULATION = "regulation"
    COMPLIANCE_REPORT = "compliance_report"
    LEGAL_DOCUMENT = "legal_document"
    FINANCIAL_STATEMENT = "financial_statement"
    INSURANCE_POLICY = "insurance_policy"
    MEDICAL_RECORD = "medical_record"
    UNKNOWN = "unknown"


class AgentResult(BaseModel):
    """Result from an agent execution"""
    output: Any
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    next_suggested_action: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = 0


class AgentStep(BaseModel):
    """Single step in agent trace"""
    step_no: int
    agent: AgentType
    tool: Optional[str] = None
    input_ref: Optional[str] = None
    output_ref: Optional[str] = None
    rationale: str
    confidence: float
    duration_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentTrace(BaseModel):
    """Complete trace of agent execution"""
    trace_id: UUID = Field(default_factory=uuid4)
    goal: str
    context: Dict[str, Any] = Field(default_factory=dict)
    steps: List[AgentStep] = Field(default_factory=list)
    status: str = "running"  # running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_duration_ms: int = 0


class Document(BaseModel):
    """Document model"""
    id: UUID = Field(default_factory=uuid4)
    filename: str
    content: str
    doc_type: Optional[DocumentType] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None


class Entity(BaseModel):
    """Extracted entity from document"""
    text: str
    label: str
    start: int
    end: int
    confidence: float
    page: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RiskFinding(BaseModel):
    """Risk/compliance finding"""
    id: UUID = Field(default_factory=uuid4)
    severity: SeverityLevel
    category: str
    description: str
    policy_reference: str
    location: Dict[str, Any]  # page, span, etc.
    confidence: float
    suggested_mitigation: Optional[str] = None
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class QAResponse(BaseModel):
    """Q&A response with citations"""
    answer: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float
    sources: List[str] = Field(default_factory=list)


class ComparisonResult(BaseModel):
    """Document comparison result"""
    doc_a_id: UUID
    doc_b_id: UUID
    semantic_diffs: List[Dict[str, Any]] = Field(default_factory=list)
    risk_delta: Dict[str, float] = Field(default_factory=dict)
    confidence: float
    summary: str


class AuditBundle(BaseModel):
    """Audit bundle for export"""
    document_id: UUID
    trace_id: UUID
    findings: List[RiskFinding] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    hash: str = ""  # For tamper evidence
