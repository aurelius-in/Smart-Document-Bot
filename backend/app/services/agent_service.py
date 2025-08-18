import asyncio
import time
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from ..agents.orchestrator import OrchestratorAgent
from ..agents.ingestion import IngestionAgent
from ..agents.classifier import ClassifierAgent
from ..agents.entity import EntityAgent
from ..agents.risk import RiskAgent
from ..agents.qa import QAAgent
from ..agents.compare import CompareAgent
from ..agents.audit import AuditAgent
from ..models.base import AgentTrace, AgentStep, Document, AgentResult
from ..core.monitoring import record_agent_execution, set_active_agents


class AgentService:
    """Service for coordinating agent execution and orchestration"""
    
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.active_traces: Dict[str, AgentTrace] = {}
        self.trace_results: Dict[str, Dict[str, Any]] = {}
        
        # Initialize all agents
        self.ingestion_agent = IngestionAgent()
        self.classifier_agent = ClassifierAgent()
        self.entity_agent = EntityAgent()
        self.risk_agent = RiskAgent()
        self.qa_agent = QAAgent()
        self.compare_agent = CompareAgent()
        self.audit_agent = AuditAgent()
        
        # Register agents with orchestrator
        self.orchestrator.register_agent(self.ingestion_agent)
        self.orchestrator.register_agent(self.classifier_agent)
        self.orchestrator.register_agent(self.entity_agent)
        self.orchestrator.register_agent(self.risk_agent)
        self.orchestrator.register_agent(self.qa_agent)
        self.orchestrator.register_agent(self.compare_agent)
        self.orchestrator.register_agent(self.audit_agent)
        
        # Update active agents count
        set_active_agents(7)
    
    async def run_agentic_pipeline(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete agentic pipeline"""
        trace_id = str(uuid4())
        
        # Create initial trace
        trace = AgentTrace(
            trace_id=UUID(trace_id),
            goal=goal,
            context=context
        )
        
        self.active_traces[trace_id] = trace
        
        try:
            # Run orchestrator
            start_time = time.time()
            result = await self.orchestrator.run(goal, context)
            duration = time.time() - start_time
            
            # Record metrics
            record_agent_execution("orchestrator", result.confidence, duration)
            
            # Store results
            self.trace_results[trace_id] = {
                "trace": trace,
                "result": result,
                "duration": duration,
                "status": "completed"
            }
            
            # Update trace
            trace.status = "completed"
            trace.completed_at = time.time()
            trace.total_duration_ms = int(duration * 1000)
            
            return {
                "trace_id": trace_id,
                "status": "completed",
                "result": result.output,
                "confidence": result.confidence,
                "duration_ms": int(duration * 1000)
            }
            
        except Exception as e:
            trace.status = "failed"
            self.trace_results[trace_id] = {
                "trace": trace,
                "error": str(e),
                "status": "failed"
            }
            
            return {
                "trace_id": trace_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def run_single_agent(self, agent_type: str, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single agent"""
        agent_map = {
            "ingestion": self.ingestion_agent,
            "classifier": self.classifier_agent,
            "entity": self.entity_agent,
            "risk": self.risk_agent,
            "qa": self.qa_agent,
            "compare": self.compare_agent,
            "audit": self.audit_agent
        }
        
        agent = agent_map.get(agent_type)
        if not agent:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        start_time = time.time()
        result = await agent.run(goal, context)
        duration = time.time() - start_time
        
        # Record metrics
        record_agent_execution(agent_type, result.confidence, duration)
        
        return {
            "agent_type": agent_type,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale,
            "duration_ms": int(duration * 1000)
        }
    
    async def process_document(self, file_path: str, goal: str = "Analyze document for compliance and risks") -> Dict[str, Any]:
        """Process a document through the complete pipeline"""
        context = {
            "file_path": file_path,
            "goal": goal
        }
        
        return await self.run_agentic_pipeline(goal, context)
    
    async def answer_question(self, question: str, document_content: str) -> Dict[str, Any]:
        """Answer a question about a document"""
        context = {
            "question": question,
            "document": Document(content=document_content)
        }
        
        return await self.run_single_agent("qa", "Answer question", context)
    
    async def compare_documents(self, doc_a_path: str, doc_b_path: str) -> Dict[str, Any]:
        """Compare two documents"""
        # First process both documents
        doc_a_result = await self.process_document(doc_a_path, "Extract document content")
        doc_b_result = await self.process_document(doc_b_path, "Extract document content")
        
        context = {
            "document_a": doc_a_result.get("result"),
            "document_b": doc_b_result.get("result")
        }
        
        return await self.run_single_agent("compare", "Compare documents", context)
    
    async def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get trace by ID"""
        return self.trace_results.get(trace_id)
    
    async def get_trace_updates(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get latest updates for a trace"""
        trace = self.active_traces.get(trace_id)
        if not trace:
            return None
        
        return {
            "trace_id": trace_id,
            "status": trace.status,
            "steps": [step.dict() for step in trace.steps],
            "total_duration_ms": trace.total_duration_ms
        }
    
    async def is_trace_complete(self, trace_id: str) -> bool:
        """Check if trace is complete"""
        trace = self.active_traces.get(trace_id)
        return trace is None or trace.status in ["completed", "failed"]
    
    async def get_all_traces(self) -> List[Dict[str, Any]]:
        """Get all traces"""
        return [
            {
                "trace_id": trace_id,
                "goal": result["trace"].goal,
                "status": result["status"],
                "created_at": result["trace"].created_at.isoformat(),
                "duration_ms": result.get("duration", 0)
            }
            for trace_id, result in self.trace_results.items()
        ]
    
    async def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of all agents"""
        return self.orchestrator.get_agent_summary()
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        return {
            "status": "healthy",
            "active_traces": len(self.active_traces),
            "total_traces": len(self.trace_results),
            "agents": await self.get_agent_summary()
        }
