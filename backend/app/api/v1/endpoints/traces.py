from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...services.agent_service import AgentService

router = APIRouter()


class AgentStep(BaseModel):
    """Agent step model"""
    id: str
    stepNumber: int
    agentType: str
    tool: str
    input: Optional[dict] = None
    output: Optional[dict] = None
    status: str
    startTime: str
    endTime: Optional[str] = None
    duration: Optional[int] = None
    confidence: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None


class AgentTrace(BaseModel):
    """Agent trace model"""
    id: str
    documentId: str
    documentName: str
    status: str
    steps: List[AgentStep] = []
    startTime: str
    endTime: Optional[str] = None
    totalDuration: Optional[int] = None
    overallConfidence: Optional[float] = None
    summary: Optional[str] = None


class StartTraceRequest(BaseModel):
    """Start trace request model"""
    documentId: str
    traceType: str = "document_processing"


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[AgentTrace]
    pagination: dict


# Mock trace storage - in production, this would be a database
TRACE_STORE = {}


@router.post("/start", response_model=AgentTrace)
async def start_agent_trace(
    request: StartTraceRequest,
    current_user: dict = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Start a new agent trace"""
    try:
        # Generate trace ID
        trace_id = f"trace_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{request.documentId[:8]}"
        
        # Create initial trace record
        trace = {
            "id": trace_id,
            "documentId": request.documentId,
            "documentName": f"Document {request.documentId}",
            "status": "running",
            "steps": [],
            "startTime": datetime.utcnow().isoformat(),
            "endTime": None,
            "totalDuration": None,
            "overallConfidence": None,
            "summary": None
        }
        
        # Store trace
        TRACE_STORE[trace_id] = trace
        
        # In a real implementation, this would start the actual agent processing
        # For now, we'll create some mock steps
        mock_steps = [
            {
                "id": f"{trace_id}_step_1",
                "stepNumber": 1,
                "agentType": "classifier",
                "tool": "document_classification",
                "input": {"document_id": request.documentId},
                "output": {"document_type": "contract", "confidence": 0.95},
                "status": "completed",
                "startTime": datetime.utcnow().isoformat(),
                "endTime": datetime.utcnow().isoformat(),
                "duration": 2000,
                "confidence": 0.95,
                "metadata": {"domain": "legal"}
            },
            {
                "id": f"{trace_id}_step_2",
                "stepNumber": 2,
                "agentType": "extractor",
                "tool": "entity_extraction",
                "input": {"document_id": request.documentId, "document_type": "contract"},
                "output": {"entities": [{"type": "party", "value": "Acme Corp"}]},
                "status": "running",
                "startTime": datetime.utcnow().isoformat(),
                "endTime": None,
                "duration": None,
                "confidence": None,
                "metadata": {"entity_count": 1}
            }
        ]
        
        trace["steps"] = mock_steps
        
        return AgentTrace(**trace)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=PaginatedResponse)
async def get_agent_traces(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """Get paginated list of agent traces"""
    try:
        # Get all traces
        traces = list(TRACE_STORE.values())
        
        # Calculate pagination
        total = len(traces)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_traces = traces[start_idx:end_idx]
        
        # Convert to AgentTrace models
        agent_traces = [
            AgentTrace(**trace) for trace in paginated_traces
        ]
        
        return PaginatedResponse(
            data=agent_traces,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trace_id}", response_model=AgentTrace)
async def get_agent_trace(
    trace_id: str,
    current_user: dict = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """Get a specific trace by ID"""
    try:
        if trace_id not in TRACE_STORE:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        trace = TRACE_STORE[trace_id]
        return AgentTrace(**trace)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trace_id}/updates")
async def get_trace_updates(
    trace_id: str,
    current_user: dict = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """Get latest updates for a trace"""
    try:
        if trace_id not in TRACE_STORE:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        trace = TRACE_STORE[trace_id]
        
        # In a real implementation, this would get real-time updates
        # For now, return the current trace state
        return {
            "trace_id": trace_id,
            "status": trace["status"],
            "steps": trace["steps"],
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trace_id}/status")
async def get_trace_status(
    trace_id: str,
    current_user: dict = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """Get trace status"""
    try:
        if trace_id not in TRACE_STORE:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        trace = TRACE_STORE[trace_id]
        is_complete = trace["status"] in ["completed", "error"]
        
        return {
            "trace_id": trace_id,
            "is_complete": is_complete,
            "status": trace["status"],
            "progress": len([s for s in trace["steps"] if s["status"] == "completed"]) / max(len(trace["steps"]), 1)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{trace_id}")
async def delete_trace(
    trace_id: str,
    current_user: dict = Depends(require_permissions(["delete"])),
    agent_service: AgentService = Depends()
):
    """Delete a trace (admin only)"""
    try:
        if trace_id not in TRACE_STORE:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        # Remove from storage
        del TRACE_STORE[trace_id]
        
        return {"message": "Trace deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_trace_stats(current_user: dict = Depends(get_current_user)):
    """Get trace statistics"""
    try:
        traces = list(TRACE_STORE.values())
        
        total_traces = len(traces)
        running_traces = len([t for t in traces if t["status"] == "running"])
        completed_traces = len([t for t in traces if t["status"] == "completed"])
        error_traces = len([t for t in traces if t["status"] == "error"])
        
        avg_duration = 0.0
        if completed_traces > 0:
            durations = [t.get("totalDuration", 0) for t in traces if t["status"] == "completed" and t.get("totalDuration")]
            avg_duration = sum(durations) / len(durations) if durations else 0
        
        avg_confidence = 0.0
        if completed_traces > 0:
            confidences = [t.get("overallConfidence", 0) for t in traces if t["status"] == "completed" and t.get("overallConfidence")]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "total_traces": total_traces,
            "running_traces": running_traces,
            "completed_traces": completed_traces,
            "error_traces": error_traces,
            "average_duration_ms": avg_duration,
            "average_confidence": avg_confidence,
            "success_rate": (completed_traces / total_traces * 100) if total_traces > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
