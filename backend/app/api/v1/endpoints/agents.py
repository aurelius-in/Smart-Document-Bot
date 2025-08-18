from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from ....services.agent_service import get_agent_service
from ....core.monitoring import monitor
from ....database.connection import get_db
from ....database.models import Document, AgentTrace

logger = logging.getLogger(__name__)
router = APIRouter()

class AgentExecutionRequest(BaseModel):
    agent_type: str
    document_content: str
    goal: str
    parameters: Optional[Dict[str, Any]] = None

class BatchAgentExecutionRequest(BaseModel):
    executions: List[AgentExecutionRequest]

class AgentCapabilityRequest(BaseModel):
    agent_type: str
    capability: str
    parameters: Optional[Dict[str, Any]] = None

@router.post("/execute")
async def execute_agent(
    request: AgentExecutionRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Execute a single agent with specified parameters"""
    
    try:
        with monitor.agent_execution(request.agent_type, "execute_agent"):
            result = await agent_service.execute_single_agent(
                agent_type=request.agent_type,
                document_content=request.document_content,
                goal=request.goal,
                **request.parameters or {}
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type=request.agent_type,
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "agent_type": request.agent_type,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in agent execution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@router.post("/batch-execute")
async def batch_execute_agents(
    request: BatchAgentExecutionRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Execute multiple agents in batch"""
    
    try:
        results = []
        
        for execution in request.executions:
            with monitor.agent_execution(execution.agent_type, "batch_execute"):
                result = await agent_service.execute_single_agent(
                    agent_type=execution.agent_type,
                    document_content=execution.document_content,
                    goal=execution.goal,
                    **execution.parameters or {}
                )
                
                results.append({
                    "agent_type": execution.agent_type,
                    "execution_id": result.execution_id,
                    "result": result.output,
                    "confidence": result.confidence,
                    "rationale": result.rationale
                })
                
                # Log the trace
                background_tasks.add_task(
                    agent_service.log_agent_trace,
                    db=db,
                    agent_type=execution.agent_type,
                    execution_id=result.execution_id,
                    input_data=execution.dict(),
                    output_data=result.output,
                    confidence=result.confidence,
                    status="completed"
                )
        
        return {
            "success": True,
            "batch_id": f"batch_{len(results)}",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in batch agent execution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch execution failed: {str(e)}")

@router.get("/capabilities")
async def get_agent_capabilities(
    agent_service = Depends(get_agent_service)
):
    """Get comprehensive information about all available agents and their capabilities"""
    
    try:
        capabilities = agent_service.get_agent_capabilities()
        
        # Add additional metadata
        enhanced_capabilities = {}
        for agent_type, agent_info in capabilities.items():
            enhanced_capabilities[agent_type] = {
                **agent_info,
                "status": "available",
                "version": "1.0.0",
                "supported_formats": ["text", "document"],
                "execution_time": "variable",
                "memory_usage": "low"
            }
        
        return {
            "success": True,
            "total_agents": len(enhanced_capabilities),
            "capabilities": enhanced_capabilities
        }
        
    except Exception as e:
        logger.error(f"Error getting agent capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")

@router.get("/status")
async def get_agents_status(
    agent_service = Depends(get_agent_service)
):
    """Get the current status of all agents"""
    
    try:
        # Get workflow status from orchestrator
        workflow_status = agent_service.get_workflow_status()
        
        # Get processing history
        processing_history = agent_service.get_all_processing_history()
        
        # Calculate agent statistics
        agent_stats = {
            "total_executions": len(processing_history),
            "successful_executions": len([h for h in processing_history if h.get("status") == "completed"]),
            "failed_executions": len([h for h in processing_history if h.get("status") == "failed"]),
            "active_processing": len([h for h in processing_history if h.get("status") == "processing"])
        }
        
        return {
            "success": True,
            "workflow_status": workflow_status,
            "agent_statistics": agent_stats,
            "recent_executions": processing_history[-10:] if processing_history else []
        }
        
    except Exception as e:
        logger.error(f"Error getting agents status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.post("/capability")
async def execute_agent_capability(
    request: AgentCapabilityRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Execute a specific capability of an agent"""
    
    try:
        # Map capability names to agent methods
        capability_mapping = {
            "summarizer": {
                "extractive": "extractive_summary_tool",
                "abstractive": "abstractive_summary_tool",
                "executive": "executive_summary_tool",
                "technical": "technical_summary_tool",
                "key_points": "key_points_tool"
            },
            "translator": {
                "translate": "translate_text_tool",
                "detect_language": "detect_language_tool",
                "technical": "technical_translation_tool",
                "cultural": "cultural_adaptation_tool"
            },
            "sentiment": {
                "analyze": "sentiment_analysis_tool",
                "tone": "tone_analysis_tool",
                "emotions": "emotion_detection_tool",
                "bias": "bias_detection_tool"
            }
        }
        
        agent_capabilities = capability_mapping.get(request.agent_type, {})
        if request.capability not in agent_capabilities:
            raise HTTPException(status_code=400, detail=f"Unknown capability: {request.capability}")
        
        # Get the agent instance
        agent_mapping = {
            "summarizer": agent_service.summarizer_agent,
            "translator": agent_service.translator_agent,
            "sentiment": agent_service.sentiment_agent
        }
        
        agent = agent_mapping.get(request.agent_type)
        if not agent:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")
        
        # Execute the capability
        method_name = agent_capabilities[request.capability]
        method = getattr(agent, method_name)
        
        with monitor.agent_execution(request.agent_type, request.capability):
            result = method(**request.parameters or {})
        
        return {
            "success": True,
            "agent_type": request.agent_type,
            "capability": request.capability,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error executing agent capability: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Capability execution failed: {str(e)}")

@router.get("/health")
async def get_agents_health():
    """Health check for all agents"""
    
    try:
        # This would typically check the health of each agent
        # For now, we'll return a simple status
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "agents": {
                "summarizer": "healthy",
                "translator": "healthy",
                "sentiment": "healthy",
                "classifier": "healthy",
                "entity": "healthy",
                "risk": "healthy",
                "qa": "healthy",
                "compare": "healthy",
                "audit": "healthy"
            }
        }
        
        return {
            "success": True,
            "health": health_status
        }
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.delete("/cleanup")
async def cleanup_old_executions(
    max_age_hours: int = 24,
    agent_service = Depends(get_agent_service)
):
    """Clean up old agent execution history"""
    
    try:
        await agent_service.cleanup_old_processing_history(max_age_hours)
        
        return {
            "success": True,
            "message": f"Cleaned up executions older than {max_age_hours} hours"
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
