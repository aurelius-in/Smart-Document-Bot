import json
import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, Document
from ..core.config import settings
from .ingestion import IngestionAgent
from .classifier import ClassifierAgent
from .entity import EntityAgent
from .risk import RiskAgent
from .qa import QAAgent
from .compare import CompareAgent
from .audit import AuditAgent

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Workflow stage enumeration"""
    PLANNING = "planning"
    INGESTION = "ingestion"
    CLASSIFICATION = "classification"
    ENTITY_EXTRACTION = "entity_extraction"
    RISK_ASSESSMENT = "risk_assessment"
    QA_GENERATION = "qa_generation"
    COMPARISON = "comparison"
    AUDIT = "audit"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowPlanningTool(Tool):
    """Tool for planning document processing workflow"""
    
    def __init__(self):
        super().__init__("plan_workflow", "Plan document processing workflow")
    
    async def execute(self, goal: str, document_info: Dict, **kwargs) -> Dict[str, Any]:
        """Plan the processing workflow"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            system_prompt = """You are an expert workflow planner for document processing. Plan the optimal processing workflow.
            
            For each workflow stage, provide:
            - stage_id: Unique stage identifier
            - stage_name: Name of the stage
            - agent_type: Type of agent to use
            - priority: HIGH/MEDIUM/LOW
            - dependencies: List of stage dependencies
            - estimated_duration: Estimated duration in seconds
            - required_inputs: Required inputs for this stage
            - expected_outputs: Expected outputs from this stage
            - success_criteria: Criteria for stage success
            - fallback_plan: Fallback plan if stage fails
            
            Also provide:
            - workflow_id: Unique workflow identifier
            - total_estimated_duration: Total estimated duration
            - critical_path: Critical path stages
            - parallel_stages: Stages that can run in parallel
            - workflow_summary: Overall workflow summary
            
            Respond with JSON:
            {
                "workflow_id": "wf_001",
                "stages": [
                    {
                        "stage_id": "stage_1",
                        "stage_name": "Document Ingestion",
                        "agent_type": "IngestionAgent",
                        "priority": "HIGH",
                        "dependencies": [],
                        "estimated_duration": 30,
                        "required_inputs": ["document_file"],
                        "expected_outputs": ["extracted_text", "metadata"],
                        "success_criteria": "Text successfully extracted",
                        "fallback_plan": "Manual text extraction"
                    }
                ],
                "total_estimated_duration": 180,
                "critical_path": ["stage_1", "stage_2", "stage_3"],
                "parallel_stages": ["stage_4", "stage_5"],
                "workflow_summary": "Comprehensive document processing workflow"
            }
            """
            
            user_prompt = f"Plan workflow for goal: {goal}\n\nDOCUMENT INFO:\n{json.dumps(document_info, indent=2)}"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await llm.agenerate([messages])
            result_text = response.generations[0][0].text.strip()
            
            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
            
            return json.loads(result_text)
            
        except Exception as e:
            return {
                "workflow_id": f"wf_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "stages": [],
                "total_estimated_duration": 0,
                "critical_path": [],
                "parallel_stages": [],
                "workflow_summary": f"Workflow planning failed: {str(e)}"
            }


class ExecutionMonitorTool(Tool):
    """Tool for monitoring workflow execution"""
    
    def __init__(self):
        super().__init__("monitor_execution", "Monitor workflow execution")
    
    async def execute(self, workflow_plan: Dict, execution_status: Dict, **kwargs) -> Dict[str, Any]:
        """Monitor workflow execution"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            system_prompt = """You are an expert workflow execution monitor. Monitor and analyze workflow execution.
            
            For each monitoring check, provide:
            - check_id: Unique check identifier
            - check_type: Type of monitoring check
            - status: PASS/FAIL/WARNING
            - description: Description of check
            - metrics: Performance metrics
            - issues: Any issues found
            - recommendations: Recommendations for improvement
            
            Also provide:
            - overall_status: Overall execution status
            - performance_score: Performance score (0.0-1.0)
            - bottlenecks: Identified bottlenecks
            - optimization_opportunities: Optimization opportunities
            - next_actions: Recommended next actions
            
            Respond with JSON:
            {
                "monitoring_checks": [
                    {
                        "check_id": "mon_001",
                        "check_type": "performance",
                        "status": "PASS",
                        "description": "Stage execution time check",
                        "metrics": {"execution_time": 25, "expected_time": 30},
                        "issues": [],
                        "recommendations": ["Continue monitoring"]
                    }
                ],
                "overall_status": "HEALTHY",
                "performance_score": 0.85,
                "bottlenecks": [],
                "optimization_opportunities": ["Parallel processing possible"],
                "next_actions": ["Proceed to next stage"]
            }
            """
            
            user_prompt = f"Monitor workflow execution:\n\nWORKFLOW PLAN:\n{json.dumps(workflow_plan, indent=2)}\n\nEXECUTION STATUS:\n{json.dumps(execution_status, indent=2)}"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await llm.agenerate([messages])
            result_text = response.generations[0][0].text.strip()
            
            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
            
            return json.loads(result_text)
            
        except Exception as e:
            return {
                "monitoring_checks": [],
                "overall_status": "UNKNOWN",
                "performance_score": 0.0,
                "bottlenecks": [f"Monitoring failed: {str(e)}"],
                "optimization_opportunities": [],
                "next_actions": ["Manual monitoring required"]
            }


class OrchestratorAgent(BaseAgent):
    """Agent responsible for orchestrating the document processing workflow"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("OrchestratorAgent", AgentType.ORCHESTRATOR)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Initialize sub-agents
        self.ingestion_agent = IngestionAgent(llm_model)
        self.classifier_agent = ClassifierAgent(llm_model)
        self.entity_agent = EntityAgent(llm_model)
        self.risk_agent = RiskAgent(llm_model)
        self.qa_agent = QAAgent(llm_model)
        self.compare_agent = CompareAgent(llm_model)
        self.audit_agent = AuditAgent(llm_model)
        
        # Add tools
        self.add_tool(WorkflowPlanningTool())
        self.add_tool(ExecutionMonitorTool())
        
        # Workflow state
        self.workflow_state = {
            "current_stage": WorkflowStage.PLANNING,
            "completed_stages": [],
            "failed_stages": [],
            "execution_history": [],
            "start_time": None,
            "end_time": None
        }
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main orchestration process"""
        document = context.get("document")
        if not document:
            return AgentResult(
                output=None,
                rationale="No document provided in context",
                confidence=0.0,
                next_suggested_action="Provide document in context"
            )
        
        try:
            # Initialize workflow
            self.workflow_state["start_time"] = datetime.utcnow()
            self.workflow_state["current_stage"] = WorkflowStage.PLANNING
            
            # Plan workflow
            planning_tool = self.get_tool("plan_workflow")
            document_info = {
                "type": document.doc_type.value if hasattr(document, 'doc_type') and document.doc_type else "unknown",
                "size": len(document.content) if hasattr(document, 'content') else 0,
                "filename": getattr(document, 'filename', 'unknown')
            }
            
            workflow_plan = await planning_tool.execute(
                goal=goal,
                document_info=document_info
            )
            
            # Execute workflow stages
            execution_results = await self._execute_workflow(workflow_plan, document, goal)
            
            # Monitor execution
            monitoring_tool = self.get_tool("monitor_execution")
            execution_status = {
                "completed_stages": self.workflow_state["completed_stages"],
                "failed_stages": self.workflow_state["failed_stages"],
                "execution_history": self.workflow_state["execution_history"]
            }
            
            monitoring_result = await monitoring_tool.execute(
                workflow_plan=workflow_plan,
                execution_status=execution_status
            )
            
            # Finalize workflow
            self.workflow_state["end_time"] = datetime.utcnow()
            self.workflow_state["current_stage"] = WorkflowStage.COMPLETED
            
            # Create orchestration result
            orchestration_result = {
                "orchestration_id": f"orch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "workflow_plan": workflow_plan,
                "execution_results": execution_results,
                "monitoring_result": monitoring_result,
                "workflow_state": self.workflow_state,
                "final_document": document
            }
            
            # Calculate confidence
            confidence = self._calculate_confidence(execution_results, monitoring_result)
            
            # Generate rationale
            completed_count = len(self.workflow_state["completed_stages"])
            failed_count = len(self.workflow_state["failed_stages"])
            total_stages = len(workflow_plan.get("stages", []))
            
            rationale = f"Orchestration completed: {completed_count}/{total_stages} stages successful, {failed_count} failed. Performance score: {monitoring_result.get('performance_score', 0.0):.2f}"
            
            return AgentResult(
                output=orchestration_result,
                rationale=rationale,
                confidence=confidence,
                next_suggested_action="Review results and address any failed stages",
                metadata={
                    "workflow_plan": workflow_plan,
                    "execution_results": execution_results,
                    "monitoring_result": monitoring_result
                }
            )
            
        except Exception as e:
            self.workflow_state["current_stage"] = WorkflowStage.FAILED
            self.workflow_state["end_time"] = datetime.utcnow()
            
            return AgentResult(
                output=None,
                rationale=f"Orchestration failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual orchestration required"
            )
    
    async def _execute_workflow(self, workflow_plan: Dict, document: Document, goal: str) -> Dict[str, Any]:
        """Execute the planned workflow"""
        execution_results = {}
        stages = workflow_plan.get("stages", [])
        
        for stage in stages:
            stage_id = stage.get("stage_id")
            stage_name = stage.get("stage_name")
            agent_type = stage.get("agent_type")
            
            try:
                # Update workflow state
                self.workflow_state["current_stage"] = WorkflowStage(stage_name.lower().replace(" ", "_"))
                
                # Execute stage
                stage_start_time = datetime.utcnow()
                stage_result = await self._execute_stage(agent_type, document, goal)
                stage_end_time = datetime.utcnow()
                
                # Record execution
                execution_record = {
                    "stage_id": stage_id,
                    "stage_name": stage_name,
                    "agent_type": agent_type,
                    "start_time": stage_start_time.isoformat(),
                    "end_time": stage_end_time.isoformat(),
                    "duration_seconds": (stage_end_time - stage_start_time).total_seconds(),
                    "status": "SUCCESS" if stage_result else "FAILED",
                    "result": stage_result
                }
                
                self.workflow_state["execution_history"].append(execution_record)
                
                if stage_result:
                    self.workflow_state["completed_stages"].append(stage_id)
                    execution_results[stage_id] = stage_result
                    
                    # Update document with stage results
                    if hasattr(stage_result, 'output') and stage_result.output:
                        if hasattr(document, 'metadata'):
                            document.metadata[f"{stage_name.lower()}_result"] = stage_result.output
                else:
                    self.workflow_state["failed_stages"].append(stage_id)
                    execution_results[stage_id] = None
                
            except Exception as e:
                # Record failure
                execution_record = {
                    "stage_id": stage_id,
                    "stage_name": stage_name,
                    "agent_type": agent_type,
                    "start_time": datetime.utcnow().isoformat(),
                    "end_time": datetime.utcnow().isoformat(),
                    "duration_seconds": 0,
                    "status": "FAILED",
                    "error": str(e)
                }
                
                self.workflow_state["execution_history"].append(execution_record)
                self.workflow_state["failed_stages"].append(stage_id)
                execution_results[stage_id] = None
        
        return execution_results
    
    async def _execute_stage(self, agent_type: str, document: Document, goal: str) -> Optional[AgentResult]:
        """Execute a single workflow stage"""
        try:
            # Map agent types to agent instances
            agent_mapping = {
                "IngestionAgent": self.ingestion_agent,
                "ClassifierAgent": self.classifier_agent,
                "EntityAgent": self.entity_agent,
                "RiskAgent": self.risk_agent,
                "QAAgent": self.qa_agent,
                "CompareAgent": self.compare_agent,
                "AuditAgent": self.audit_agent
            }
            
            agent = agent_mapping.get(agent_type)
            if not agent:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            # Prepare context for the agent
            context = {
                "document": document,
                "goal": goal,
                "orchestrator": self,
                "workflow_state": self.workflow_state
            }
            
            # Execute agent with timeout
            import asyncio
            try:
                result = await asyncio.wait_for(
                    agent.run(goal, context),
                    timeout=settings.AGENT_TIMEOUT
                )
                return result
            except asyncio.TimeoutError:
                raise Exception(f"Agent {agent_type} execution timed out after {settings.AGENT_TIMEOUT} seconds")
            
        except Exception as e:
            logger.error(f"Stage execution failed for {agent_type}: {str(e)}")
            return None
    
    def _calculate_confidence(self, execution_results: Dict, monitoring_result: Dict) -> float:
        """Calculate confidence based on execution results"""
        confidence = 0.5  # Base confidence
        
        # Execution success rate
        total_stages = len(execution_results)
        successful_stages = len([r for r in execution_results.values() if r is not None])
        
        if total_stages > 0:
            success_rate = successful_stages / total_stages
            confidence += success_rate * 0.3
        
        # Performance score
        performance_score = monitoring_result.get("performance_score", 0.0)
        confidence += performance_score * 0.2
        
        # Overall status
        overall_status = monitoring_result.get("overall_status", "UNKNOWN")
        if overall_status == "HEALTHY":
            confidence += 0.2
        elif overall_status == "WARNING":
            confidence += 0.1
        
        # Bottlenecks and issues
        bottlenecks = monitoring_result.get("bottlenecks", [])
        if not bottlenecks:
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "current_stage": self.workflow_state["current_stage"].value,
            "completed_stages": self.workflow_state["completed_stages"],
            "failed_stages": self.workflow_state["failed_stages"],
            "total_execution_time": self._calculate_total_execution_time(),
            "progress_percentage": self._calculate_progress_percentage()
        }
    
    def _calculate_total_execution_time(self) -> float:
        """Calculate total execution time"""
        if not self.workflow_state["start_time"]:
            return 0.0
        
        end_time = self.workflow_state["end_time"] or datetime.utcnow()
        return (end_time - self.workflow_state["start_time"]).total_seconds()
    
    def _calculate_progress_percentage(self) -> float:
        """Calculate workflow progress percentage"""
        total_stages = len(self.workflow_state["completed_stages"]) + len(self.workflow_state["failed_stages"])
        
        if total_stages == 0:
            return 0.0
        
        completed = len(self.workflow_state["completed_stages"])
        return (completed / total_stages) * 100.0
