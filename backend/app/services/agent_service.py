import asyncio
import uuid
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

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
from ..core.monitoring import get_monitor

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing agent execution and orchestration"""
    
    def __init__(self):
        self.monitor = get_monitor()
        self.processing_history = {}
        self.agent_instances = {}
        self.is_initialized = False
        
        # Agent mapping for easy access
        self.agent_mapping = {
            "orchestrator": None,
            "ingestion": None,
            "classifier": None,
            "entity": None,
            "risk": None,
            "qa": None,
            "compare": None,
            "audit": None,
            "summarizer": None,
            "translator": None,
            "sentiment": None
        }
    
    async def initialize(self) -> None:
        """Initialize all agents and services"""
        try:
            logger.info("Initializing AgentService...")
            
            # Initialize orchestrator agent
            self.agent_mapping["orchestrator"] = OrchestratorAgent(
                llm_model=settings.OPENAI_MODEL
            )
            
            # Initialize individual agents
            self.agent_mapping["ingestion"] = IngestionAgent(
                llm_model=settings.OPENAI_MODEL
            )
            self.agent_mapping["classifier"] = ClassifierAgent(
                llm_model=settings.OPENAI_MODEL
            )
            self.agent_mapping["entity"] = EntityAgent(
                llm_model=settings.OPENAI_MODEL
            )
            self.agent_mapping["risk"] = RiskAgent(
                llm_model=settings.OPENAI_MODEL
            )
            self.agent_mapping["qa"] = QAAgent(
                llm_model=settings.OPENAI_MODEL
            )
            self.agent_mapping["compare"] = CompareAgent(
                llm_model=settings.OPENAI_MODEL
            )
            self.agent_mapping["audit"] = AuditAgent(
                llm_model=settings.OPENAI_MODEL
            )
            self.agent_mapping["summarizer"] = SummarizerAgent(
                llm_model=settings.OPENAI_MODEL
            )
            self.agent_mapping["translator"] = TranslatorAgent(
                llm_model=settings.OPENAI_MODEL
            )
            self.agent_mapping["sentiment"] = SentimentAnalysisAgent(
                llm_model=settings.OPENAI_MODEL
            )
            
            # Store references for backward compatibility
            self.orchestrator = self.agent_mapping["orchestrator"]
            self.ingestion_agent = self.agent_mapping["ingestion"]
            self.classifier_agent = self.agent_mapping["classifier"]
            self.entity_agent = self.agent_mapping["entity"]
            self.risk_agent = self.agent_mapping["risk"]
            self.qa_agent = self.agent_mapping["qa"]
            self.compare_agent = self.agent_mapping["compare"]
            self.audit_agent = self.agent_mapping["audit"]
            self.summarizer_agent = self.agent_mapping["summarizer"]
            self.translator_agent = self.agent_mapping["translator"]
            self.sentiment_agent = self.agent_mapping["sentiment"]
            
            self.is_initialized = True
            logger.info("AgentService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AgentService: {e}")
            raise
    
    async def process_document(self, document: Document, goal: str = "Analyze document for compliance and risks") -> Dict[str, Any]:
        """Process a document through the complete agent pipeline"""
        if not self.is_initialized:
            raise RuntimeError("AgentService not initialized. Call initialize() first.")
        
        processing_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting document processing: {processing_id}")
            
            # Initialize processing history
            self.processing_history[processing_id] = {
                "processing_id": processing_id,
                "start_time": start_time.isoformat(),
                "document_id": getattr(document, 'id', 'unknown'),
                "goal": goal,
                "stages": [],
                "status": "processing"
            }
            
            # Prepare context for orchestrator
            context = {
                "document": document,
                "processing_id": processing_id,
                "goal": goal,
                "agent_service": self
            }
            
            # Execute orchestration with monitoring
            with self.monitor.monitor_agent_execution("orchestrator", processing_id):
                orchestration_result = await self.orchestrator.run(goal, context)
            
            # Calculate processing time
            end_time = datetime.utcnow()
            processing_duration = (end_time - start_time).total_seconds()
            
            # Update processing history
            self.processing_history[processing_id].update({
                "end_time": end_time.isoformat(),
                "duration": processing_duration,
                "status": "completed" if orchestration_result else "failed",
                "orchestration_result": orchestration_result.dict() if orchestration_result else None,
                "workflow_status": self.orchestrator.get_workflow_status()
            })
            
            # Record metrics
            self.monitor.record_agent_execution(
                agent_name="orchestrator",
                duration=processing_duration,
                success=bool(orchestration_result),
                confidence=orchestration_result.confidence if orchestration_result else 0.0
            )
            
            logger.info(f"Document processing completed: {processing_id} in {processing_duration:.2f}s")
            
            return {
                "processing_id": processing_id,
                "status": "completed" if orchestration_result else "failed",
                "result": orchestration_result.output if orchestration_result else None,
                "confidence": orchestration_result.confidence if orchestration_result else 0.0,
                "rationale": orchestration_result.rationale if orchestration_result else "Processing failed",
                "workflow_status": self.orchestrator.get_workflow_status(),
                "duration": processing_duration
            }
            
        except Exception as e:
            end_time = datetime.utcnow()
            processing_duration = (end_time - start_time).total_seconds()
            
            logger.error(f"Document processing failed: {processing_id} - {e}")
            
            # Update processing history with error
            if processing_id in self.processing_history:
                self.processing_history[processing_id].update({
                    "end_time": end_time.isoformat(),
                    "duration": processing_duration,
                    "status": "failed",
                    "error": str(e)
                })
            
            # Record error metrics
            self.monitor.record_agent_execution(
                agent_name="orchestrator",
                duration=processing_duration,
                success=False,
                error=str(e)
            )
            
            return {
                "processing_id": processing_id,
                "status": "failed",
                "error": str(e),
                "result": None,
                "confidence": 0.0,
                "rationale": f"Processing failed: {str(e)}",
                "duration": processing_duration
            }
    
    async def execute_single_agent(self, agent_type: str, document: Document, goal: str) -> AgentResult:
        """Execute a single agent with monitoring and error handling"""
        if not self.is_initialized:
            raise RuntimeError("AgentService not initialized. Call initialize() first.")
        
        agent_type = agent_type.lower()
        if agent_type not in self.agent_mapping:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent = self.agent_mapping[agent_type]
        if not agent:
            raise RuntimeError(f"Agent {agent_type} not initialized")
        
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Executing agent: {agent_type}")
            
            # Prepare context
            context = {
                "document": document,
                "goal": goal,
                "agent_service": self
            }
            
            # Execute agent with monitoring
            with self.monitor.monitor_agent_execution(agent_type, f"{agent_type}_{document.id}"):
                result = await agent.run(goal, context)
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_duration = (end_time - start_time).total_seconds()
            
            # Record metrics
            self.monitor.record_agent_execution(
                agent_name=agent_type,
                duration=execution_duration,
                success=bool(result),
                confidence=result.confidence if result else 0.0
            )
            
            logger.info(f"Agent execution completed: {agent_type} in {execution_duration:.2f}s")
            return result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_duration = (end_time - start_time).total_seconds()
            
            logger.error(f"Agent execution failed: {agent_type} - {e}")
            
            # Record error metrics
            self.monitor.record_agent_execution(
                agent_name=agent_type,
                duration=execution_duration,
                success=False,
                error=str(e)
            )
            
            return AgentResult(
                output=None,
                rationale=f"Agent execution failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual processing required"
            )
    
    async def compare_documents(self, document_a: Document, document_b: Document, goal: str = "Compare documents for differences and risk changes") -> Dict[str, Any]:
        """Compare two documents using the compare agent"""
        if not self.is_initialized:
            raise RuntimeError("AgentService not initialized. Call initialize() first.")
        
        start_time = datetime.utcnow()
        
        try:
            logger.info("Starting document comparison")
            
            # Prepare context for comparison
            context = {
                "document_a": document_a,
                "document_b": document_b,
                "goal": goal,
                "agent_service": self
            }
            
            # Execute comparison with monitoring
            with self.monitor.monitor_agent_execution("compare", f"compare_{document_a.id}_{document_b.id}"):
                comparison_result = await self.compare_agent.run(goal, context)
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_duration = (end_time - start_time).total_seconds()
            
            # Record metrics
            self.monitor.record_agent_execution(
                agent_name="compare",
                duration=execution_duration,
                success=bool(comparison_result),
                confidence=comparison_result.confidence if comparison_result else 0.0
            )
            
            logger.info(f"Document comparison completed in {execution_duration:.2f}s")
            
            return {
                "status": "completed" if comparison_result else "failed",
                "result": comparison_result.output if comparison_result else None,
                "confidence": comparison_result.confidence if comparison_result else 0.0,
                "rationale": comparison_result.rationale if comparison_result else "Comparison failed",
                "duration": execution_duration
            }
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_duration = (end_time - start_time).total_seconds()
            
            logger.error(f"Document comparison failed: {e}")
            
            # Record error metrics
            self.monitor.record_agent_execution(
                agent_name="compare",
                duration=execution_duration,
                success=False,
                error=str(e)
            )
            
            return {
                "status": "failed",
                "error": str(e),
                "result": None,
                "confidence": 0.0,
                "rationale": f"Comparison failed: {str(e)}",
                "duration": execution_duration
            }
    
    async def generate_audit_trail(self, document: Document, processing_history: List[Dict] = None) -> Dict[str, Any]:
        """Generate audit trail for a document"""
        if not self.is_initialized:
            raise RuntimeError("AgentService not initialized. Call initialize() first.")
        
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Generating audit trail for document: {document.id}")
            
            # Prepare context for audit
            context = {
                "document": document,
                "processing_history": processing_history or [],
                "goal": "Generate comprehensive audit trail",
                "agent_service": self
            }
            
            # Execute audit with monitoring
            with self.monitor.monitor_agent_execution("audit", f"audit_{document.id}"):
                audit_result = await self.audit_agent.run("Generate audit trail", context)
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_duration = (end_time - start_time).total_seconds()
            
            # Record metrics
            self.monitor.record_agent_execution(
                agent_name="audit",
                duration=execution_duration,
                success=bool(audit_result),
                confidence=audit_result.confidence if audit_result else 0.0
            )
            
            logger.info(f"Audit trail generation completed in {execution_duration:.2f}s")
            
            return {
                "status": "completed" if audit_result else "failed",
                "result": audit_result.output if audit_result else None,
                "confidence": audit_result.confidence if audit_result else 0.0,
                "rationale": audit_result.rationale if audit_result else "Audit generation failed",
                "duration": execution_duration
            }
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_duration = (end_time - start_time).total_seconds()
            
            logger.error(f"Audit trail generation failed: {e}")
            
            # Record error metrics
            self.monitor.record_agent_execution(
                agent_name="audit",
                duration=execution_duration,
                success=False,
                error=str(e)
            )
            
            return {
                "status": "failed",
                "error": str(e),
                "result": None,
                "confidence": 0.0,
                "rationale": f"Audit generation failed: {str(e)}",
                "duration": execution_duration
            }
    
    async def generate_qa(self, document: Document, goal: str = "Generate questions and answers about the document") -> Dict[str, Any]:
        """Generate questions and answers for a document"""
        if not self.is_initialized:
            raise RuntimeError("AgentService not initialized. Call initialize() first.")
        
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Generating QA for document: {document.id}")
            
            # Prepare context for QA generation
            context = {
                "document": document,
                "goal": goal,
                "agent_service": self
            }
            
            # Execute QA generation with monitoring
            with self.monitor.monitor_agent_execution("qa", f"qa_{document.id}"):
                qa_result = await self.qa_agent.run(goal, context)
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_duration = (end_time - start_time).total_seconds()
            
            # Record metrics
            self.monitor.record_agent_execution(
                agent_name="qa",
                duration=execution_duration,
                success=bool(qa_result),
                confidence=qa_result.confidence if qa_result else 0.0
            )
            
            logger.info(f"QA generation completed in {execution_duration:.2f}s")
            
            return {
                "status": "completed" if qa_result else "failed",
                "result": qa_result.output if qa_result else None,
                "confidence": qa_result.confidence if qa_result else 0.0,
                "rationale": qa_result.rationale if qa_result else "QA generation failed",
                "duration": execution_duration
            }
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_duration = (end_time - start_time).total_seconds()
            
            logger.error(f"QA generation failed: {e}")
            
            # Record error metrics
            self.monitor.record_agent_execution(
                agent_name="qa",
                duration=execution_duration,
                success=False,
                error=str(e)
            )
            
            return {
                "status": "failed",
                "error": str(e),
                "result": None,
                "confidence": 0.0,
                "rationale": f"QA generation failed: {str(e)}",
                "duration": execution_duration
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
                "capabilities": ["Workflow planning", "Execution monitoring", "Stage coordination"],
                "status": "initialized" if self.agent_mapping["orchestrator"] else "not_initialized"
            },
            "ingestion": {
                "name": "IngestionAgent",
                "description": "Extracts and normalizes text from documents",
                "capabilities": ["OCR", "PDF parsing", "Text normalization"],
                "status": "initialized" if self.agent_mapping["ingestion"] else "not_initialized"
            },
            "classifier": {
                "name": "ClassifierAgent",
                "description": "Classifies documents and analyzes content structure",
                "capabilities": ["Document classification", "Content analysis", "Domain identification"],
                "status": "initialized" if self.agent_mapping["classifier"] else "not_initialized"
            },
            "entity": {
                "name": "EntityAgent",
                "description": "Extracts named entities and key information",
                "capabilities": ["Named entity recognition", "Clause extraction", "Key information extraction"],
                "status": "initialized" if self.agent_mapping["entity"] else "not_initialized"
            },
            "risk": {
                "name": "RiskAgent",
                "description": "Assesses compliance, financial, and operational risks",
                "capabilities": ["Compliance risk analysis", "Financial risk analysis", "Operational risk analysis"],
                "status": "initialized" if self.agent_mapping["risk"] else "not_initialized"
            },
            "qa": {
                "name": "QAAgent",
                "description": "Generates questions and answers about documents",
                "capabilities": ["Factual question generation", "Compliance question generation", "Risk question generation"],
                "status": "initialized" if self.agent_mapping["qa"] else "not_initialized"
            },
            "compare": {
                "name": "CompareAgent",
                "description": "Compares documents for differences and changes",
                "capabilities": ["Semantic comparison", "Structural comparison", "Compliance comparison"],
                "status": "initialized" if self.agent_mapping["compare"] else "not_initialized"
            },
            "audit": {
                "name": "AuditAgent",
                "description": "Generates audit trails and compliance reports",
                "capabilities": ["Audit trail generation", "Compliance reporting", "Audit bundle creation"],
                "status": "initialized" if self.agent_mapping["audit"] else "not_initialized"
            },
            "summarizer": {
                "name": "SummarizerAgent",
                "description": "Generates comprehensive document summaries",
                "capabilities": ["Extractive summarization", "Abstractive summarization", "Executive summaries", "Technical summaries", "Key points extraction"],
                "status": "initialized" if self.agent_mapping["summarizer"] else "not_initialized"
            },
            "translator": {
                "name": "TranslatorAgent",
                "description": "Translates documents between multiple languages",
                "capabilities": ["Text translation", "Document translation", "Language detection", "Technical translation", "Cultural adaptation"],
                "status": "initialized" if self.agent_mapping["translator"] else "not_initialized"
            },
            "sentiment": {
                "name": "SentimentAnalysisAgent",
                "description": "Analyzes sentiment, tone, and emotional content",
                "capabilities": ["Sentiment analysis", "Tone analysis", "Emotion detection", "Bias detection", "Sentiment tracking"],
                "status": "initialized" if self.agent_mapping["sentiment"] else "not_initialized"
            }
        }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status from orchestrator"""
        if not self.orchestrator:
            return {"status": "not_initialized"}
        return self.orchestrator.get_workflow_status()
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        return {
            "initialized": self.is_initialized,
            "agents": self.get_agent_capabilities(),
            "processing_history_count": len(self.processing_history),
            "workflow_status": self.get_workflow_status(),
            "monitoring": {
                "enabled": True,
                "metrics_available": True
            }
        }
    
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
        
        logger.info(f"Cleaned up {len(to_remove)} old processing history entries")
    
    async def cleanup(self) -> None:
        """Cleanup resources and connections"""
        try:
            logger.info("Cleaning up AgentService...")
            
            # Clean up processing history
            await self.cleanup_old_processing_history()
            
            # Clear agent instances
            self.agent_mapping.clear()
            self.processing_history.clear()
            
            self.is_initialized = False
            logger.info("AgentService cleanup completed")
            
        except Exception as e:
            logger.error(f"AgentService cleanup failed: {e}")
            raise
