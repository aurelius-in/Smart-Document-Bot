import asyncio
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..agents.orchestrator import OrchestratorAgent
from ..agents.ingestion import IngestionAgent
from ..agents.classifier import ClassifierAgent
from ..agents.entity import EntityAgent
from ..agents.risk import RiskAgent
from ..agents.qa import QAAgent
from ..agents.compare import CompareAgent
from ..agents.audit import AuditAgent
from ..agents.summarizer import SummarizerAgent
from ..agents.translator import TranslatorAgent
from ..agents.sentiment import SentimentAnalysisAgent
from ..models.base import Document, AgentResult, AgentType
from ..core.config import settings


class AgentService:
    """Service for managing agent execution and orchestration"""
    
    def __init__(self):
        # Initialize the orchestrator agent
        self.orchestrator = OrchestratorAgent(llm_model=settings.LLM_MODEL)
        
        # Initialize individual agents for direct access
        self.ingestion_agent = IngestionAgent(llm_model=settings.LLM_MODEL)
        self.classifier_agent = ClassifierAgent(llm_model=settings.LLM_MODEL)
        self.entity_agent = EntityAgent(llm_model=settings.LLM_MODEL)
        self.risk_agent = RiskAgent(llm_model=settings.LLM_MODEL)
        self.qa_agent = QAAgent(llm_model=settings.LLM_MODEL)
        self.compare_agent = CompareAgent(llm_model=settings.LLM_MODEL)
        self.audit_agent = AuditAgent(llm_model=settings.LLM_MODEL)
        self.summarizer_agent = SummarizerAgent(llm_model=settings.LLM_MODEL)
        self.translator_agent = TranslatorAgent(llm_model=settings.LLM_MODEL)
        self.sentiment_agent = SentimentAnalysisAgent(llm_model=settings.LLM_MODEL)
        
        # Processing history
        self.processing_history = {}
    
    async def process_document(self, document: Document, goal: str = "Analyze document for compliance and risks") -> Dict[str, Any]:
        """Process a document through the complete agent pipeline"""
        try:
            # Generate processing ID
            processing_id = str(uuid.uuid4())
            
            # Initialize processing history
            self.processing_history[processing_id] = {
                "processing_id": processing_id,
                "start_time": datetime.utcnow().isoformat(),
                "document_id": getattr(document, 'id', 'unknown'),
                "goal": goal,
                "stages": [],
                "status": "processing"
            }
            
            # Prepare context for orchestrator
            context = {
                "document": document,
                "processing_id": processing_id,
                "goal": goal
            }
            
            # Execute orchestration
            orchestration_result = await self.orchestrator.run(goal, context)
            
            # Update processing history
            self.processing_history[processing_id].update({
                "end_time": datetime.utcnow().isoformat(),
                "status": "completed" if orchestration_result else "failed",
                "orchestration_result": orchestration_result.dict() if orchestration_result else None,
                "workflow_status": self.orchestrator.get_workflow_status()
            })
            
            return {
                "processing_id": processing_id,
                "status": "completed" if orchestration_result else "failed",
                "result": orchestration_result.output if orchestration_result else None,
                "confidence": orchestration_result.confidence if orchestration_result else 0.0,
                "rationale": orchestration_result.rationale if orchestration_result else "Processing failed",
                "workflow_status": self.orchestrator.get_workflow_status()
            }
            
        except Exception as e:
            # Update processing history with error
            if processing_id in self.processing_history:
                self.processing_history[processing_id].update({
                    "end_time": datetime.utcnow().isoformat(),
                    "status": "failed",
                    "error": str(e)
                })
            
            return {
                "processing_id": processing_id if 'processing_id' in locals() else "unknown",
                "status": "failed",
                "error": str(e),
                "result": None,
                "confidence": 0.0,
                "rationale": f"Processing failed: {str(e)}"
            }
    
    async def execute_single_agent(self, agent_type: str, document: Document, goal: str) -> AgentResult:
        """Execute a single agent"""
        try:
            # Map agent types to agent instances
            agent_mapping = {
                "ingestion": self.ingestion_agent,
                "classifier": self.classifier_agent,
                "entity": self.entity_agent,
                "risk": self.risk_agent,
                "qa": self.qa_agent,
                "compare": self.compare_agent,
                "audit": self.audit_agent,
                "summarizer": self.summarizer_agent,
                "translator": self.translator_agent,
                "sentiment": self.sentiment_agent
            }
            
            agent = agent_mapping.get(agent_type.lower())
            if not agent:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            # Prepare context
            context = {
                "document": document,
                "goal": goal
            }
            
            # Execute agent
            result = await agent.run(goal, context)
            return result
            
        except Exception as e:
            return AgentResult(
                output=None,
                rationale=f"Agent execution failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual processing required"
            )
    
    async def compare_documents(self, document_a: Document, document_b: Document, goal: str = "Compare documents for differences and risk changes") -> Dict[str, Any]:
        """Compare two documents using the compare agent"""
        try:
            # Prepare context for comparison
            context = {
                "document_a": document_a,
                "document_b": document_b,
                "goal": goal
            }
            
            # Execute comparison
            comparison_result = await self.compare_agent.run(goal, context)
            
            return {
                "status": "completed" if comparison_result else "failed",
                "result": comparison_result.output if comparison_result else None,
                "confidence": comparison_result.confidence if comparison_result else 0.0,
                "rationale": comparison_result.rationale if comparison_result else "Comparison failed"
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "result": None,
                "confidence": 0.0,
                "rationale": f"Comparison failed: {str(e)}"
            }
    
    async def generate_audit_trail(self, document: Document, processing_history: List[Dict] = None) -> Dict[str, Any]:
        """Generate audit trail for a document"""
        try:
            # Prepare context for audit
            context = {
                "document": document,
                "processing_history": processing_history or [],
                "goal": "Generate comprehensive audit trail"
            }
            
            # Execute audit
            audit_result = await self.audit_agent.run("Generate audit trail", context)
            
            return {
                "status": "completed" if audit_result else "failed",
                "result": audit_result.output if audit_result else None,
                "confidence": audit_result.confidence if audit_result else 0.0,
                "rationale": audit_result.rationale if audit_result else "Audit generation failed"
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "result": None,
                "confidence": 0.0,
                "rationale": f"Audit generation failed: {str(e)}"
            }
    
    async def generate_qa(self, document: Document, goal: str = "Generate questions and answers about the document") -> Dict[str, Any]:
        """Generate questions and answers for a document"""
        try:
            # Prepare context for QA generation
            context = {
                "document": document,
                "goal": goal
            }
            
            # Execute QA generation
            qa_result = await self.qa_agent.run(goal, context)
            
            return {
                "status": "completed" if qa_result else "failed",
                "result": qa_result.output if qa_result else None,
                "confidence": qa_result.confidence if qa_result else 0.0,
                "rationale": qa_result.rationale if qa_result else "QA generation failed"
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "result": None,
                "confidence": 0.0,
                "rationale": f"QA generation failed: {str(e)}"
            }
    
    def get_processing_status(self, processing_id: str) -> Optional[Dict[str, Any]]:
        """Get processing status for a given ID"""
        return self.processing_history.get(processing_id)
    
    def get_all_processing_history(self) -> List[Dict[str, Any]]:
        """Get all processing history"""
        return list(self.processing_history.values())
    
    def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get information about available agents and their capabilities"""
        return {
            "orchestrator": {
                "name": "OrchestratorAgent",
                "description": "Coordinates the complete document processing workflow",
                "capabilities": ["Workflow planning", "Execution monitoring", "Stage coordination"]
            },
            "ingestion": {
                "name": "IngestionAgent",
                "description": "Extracts and normalizes text from documents",
                "capabilities": ["OCR", "PDF parsing", "Text normalization"]
            },
            "classifier": {
                "name": "ClassifierAgent",
                "description": "Classifies documents and analyzes content structure",
                "capabilities": ["Document classification", "Content analysis", "Domain identification"]
            },
            "entity": {
                "name": "EntityAgent",
                "description": "Extracts named entities and key information",
                "capabilities": ["Named entity recognition", "Clause extraction", "Key information extraction"]
            },
            "risk": {
                "name": "RiskAgent",
                "description": "Assesses compliance, financial, and operational risks",
                "capabilities": ["Compliance risk analysis", "Financial risk analysis", "Operational risk analysis"]
            },
            "qa": {
                "name": "QAAgent",
                "description": "Generates questions and answers about documents",
                "capabilities": ["Factual question generation", "Compliance question generation", "Risk question generation"]
            },
            "compare": {
                "name": "CompareAgent",
                "description": "Compares documents for differences and changes",
                "capabilities": ["Semantic comparison", "Structural comparison", "Compliance comparison"]
            },
            "audit": {
                "name": "AuditAgent",
                "description": "Generates audit trails and compliance reports",
                "capabilities": ["Audit trail generation", "Compliance reporting", "Audit bundle creation"]
            },
            "summarizer": {
                "name": "SummarizerAgent",
                "description": "Generates comprehensive document summaries",
                "capabilities": ["Extractive summarization", "Abstractive summarization", "Executive summaries", "Technical summaries", "Key points extraction"]
            },
            "translator": {
                "name": "TranslatorAgent",
                "description": "Translates documents between multiple languages",
                "capabilities": ["Text translation", "Document translation", "Language detection", "Technical translation", "Cultural adaptation"]
            },
            "sentiment": {
                "name": "SentimentAnalysisAgent",
                "description": "Analyzes sentiment, tone, and emotional content",
                "capabilities": ["Sentiment analysis", "Tone analysis", "Emotion detection", "Bias detection", "Sentiment tracking"]
            }
        }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status from orchestrator"""
        return self.orchestrator.get_workflow_status()
    
    async def cleanup_old_processing_history(self, max_age_hours: int = 24):
        """Clean up old processing history"""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        to_remove = []
        for processing_id, history in self.processing_history.items():
            start_time = datetime.fromisoformat(history["start_time"].replace('Z', '+00:00')).timestamp()
            if start_time < cutoff_time:
                to_remove.append(processing_id)
        
        for processing_id in to_remove:
            del self.processing_history[processing_id]
