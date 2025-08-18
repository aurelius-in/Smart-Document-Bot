from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...services.agent_service import AgentService

router = APIRouter()


class AgenticRequest(BaseModel):
    """Request model for agentic processing"""
    goal: str
    context: Dict[str, Any] = {}
    file_path: Optional[str] = None
    document_content: Optional[str] = None


class AgenticResponse(BaseModel):
    """Response model for agentic processing"""
    trace_id: str
    status: str
    confidence: float
    duration_ms: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/run", response_model=AgenticResponse)
async def run_agentic_pipeline(
    request: AgenticRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Run the complete agentic pipeline"""
    try:
        # Add user context
        request.context["user"] = current_user
        
        # Run the pipeline
        result = await agent_service.run_agentic_pipeline(
            goal=request.goal,
            context=request.context
        )
        
        return AgenticResponse(
            trace_id=result["trace_id"],
            status=result["status"],
            confidence=result.get("confidence", 0.0),
            duration_ms=result.get("duration_ms", 0),
            result=result.get("result"),
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/single-agent/{agent_type}")
async def run_single_agent(
    agent_type: str,
    request: AgenticRequest,
    current_user: str = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Run a single agent"""
    try:
        result = await agent_service.run_single_agent(
            agent_type=agent_type,
            goal=request.goal,
            context=request.context
        )
        
        return {
            "agent_type": agent_type,
            "status": "completed",
            "confidence": result["confidence"],
            "duration_ms": result["duration_ms"],
            "result": result["result"],
            "rationale": result["rationale"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_agent_health(
    current_user: str = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """Get agent system health"""
    try:
        health = await agent_service.get_system_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_agent_summary(
    current_user: str = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """Get summary of all agents"""
    try:
        summary = await agent_service.get_agent_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
