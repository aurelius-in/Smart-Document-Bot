import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...services.agent_service import AgentService

router = APIRouter()

class AgentStep(BaseModel):
    """Agent step model"""
    stepId: str
    agentType: str
    status: str
    startTime: str
    endTime: Optional[str] = None
    duration: Optional[int] = None
    confidence: Optional[float] = None
    rationale: Optional[str] = None
    output: Optional[dict] = None
    error: Optional[str] = None

class AgentTrace(BaseModel):
    """Agent trace model"""
    traceId: str
    goal: str
    status: str
    startTime: str
    endTime: Optional[str] = None
    totalDuration: Optional[int] = None
    steps: List[AgentStep]
    overallConfidence: Optional[float] = None
    workflowStatus: Optional[dict] = None

class StartTraceRequest(BaseModel):
    """Start trace request model"""
    goal: str
    documentId: Optional[str] = None

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[AgentTrace]
    pagination: dict

# Mock trace storage
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
        trace_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Create initial trace record
        trace_record = {
            "traceId": trace_id,
            "goal": request.goal,
            "status": "running",
            "startTime": start_time.isoformat(),
            "endTime": None,
            "totalDuration": None,
            "steps": [],
            "overallConfidence": None,
            "workflowStatus": None,
            "createdBy": current_user["email"],
            "documentId": request.documentId
        }
        
        TRACE_STORE[trace_id] = trace_record
        
        # If document ID is provided, start processing
        if request.documentId:
            # Import document store from documents endpoint
            from .documents import DOCUMENT_STORE
            
            if request.documentId in DOCUMENT_STORE:
                document = DOCUMENT_STORE[request.documentId]["document"]
                
                # Start processing in background (in production, this would be async)
                # For now, we'll simulate the process
                trace_record["status"] = "processing"
                trace_record["workflowStatus"] = agent_service.get_workflow_status()
        
        return AgentTrace(**trace_record)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start trace: {str(e)}")

@router.get("/", response_model=PaginatedResponse)
async def get_agent_traces(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of agent traces"""
    try:
        # Filter traces by user
        user_traces = [
            trace for trace in TRACE_STORE.values()
            if trace.get("createdBy") == current_user["email"]
        ]
        
        # Calculate pagination
        total = len(user_traces)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # Get page of traces
        page_traces = user_traces[start_idx:end_idx]
        
        # Convert to AgentTrace
        trace_results = []
        for trace in page_traces:
            agent_trace = AgentTrace(
                traceId=trace["traceId"],
                goal=trace["goal"],
                status=trace["status"],
                startTime=trace["startTime"],
                endTime=trace.get("endTime"),
                totalDuration=trace.get("totalDuration"),
                steps=trace.get("steps", []),
                overallConfidence=trace.get("overallConfidence"),
                workflowStatus=trace.get("workflowStatus")
            )
            trace_results.append(agent_trace)
        
        return PaginatedResponse(
            data=trace_results,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve traces: {str(e)}")

@router.get("/{trace_id}", response_model=AgentTrace)
async def get_agent_trace(
    trace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific agent trace"""
    try:
        if trace_id not in TRACE_STORE:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        trace = TRACE_STORE[trace_id]
        
        # Check if user has access to this trace
        if trace.get("createdBy") != current_user["email"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return AgentTrace(
            traceId=trace["traceId"],
            goal=trace["goal"],
            status=trace["status"],
            startTime=trace["startTime"],
            endTime=trace.get("endTime"),
            totalDuration=trace.get("totalDuration"),
            steps=trace.get("steps", []),
            overallConfidence=trace.get("overallConfidence"),
            workflowStatus=trace.get("workflowStatus")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trace: {str(e)}")

@router.get("/{trace_id}/updates")
async def get_trace_updates(
    trace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get real-time updates for a trace"""
    try:
        if trace_id not in TRACE_STORE:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        trace = TRACE_STORE[trace_id]
        
        # Check if user has access to this trace
        if trace.get("createdBy") != current_user["email"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get processing history from agent service
        agent_service = AgentService()
        processing_history = agent_service.get_all_processing_history()
        
        # Find relevant processing history
        relevant_history = [
            h for h in processing_history
            if h.get("document_id") == trace.get("documentId")
        ]
        
        return {
            "traceId": trace_id,
            "status": trace["status"],
            "currentStep": len(trace.get("steps", [])),
            "totalSteps": len(trace.get("steps", [])),
            "progress": trace.get("progress", 0.0),
            "lastUpdate": datetime.utcnow().isoformat(),
            "processingHistory": relevant_history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trace updates: {str(e)}")

@router.get("/{trace_id}/status")
async def get_trace_status(
    trace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get current status of a trace"""
    try:
        if trace_id not in TRACE_STORE:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        trace = TRACE_STORE[trace_id]
        
        # Check if user has access to this trace
        if trace.get("createdBy") != current_user["email"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get workflow status from agent service
        agent_service = AgentService()
        workflow_status = agent_service.get_workflow_status()
        
        return {
            "traceId": trace_id,
            "status": trace["status"],
            "goal": trace["goal"],
            "startTime": trace["startTime"],
            "endTime": trace.get("endTime"),
            "totalDuration": trace.get("totalDuration"),
            "overallConfidence": trace.get("overallConfidence"),
            "workflowStatus": workflow_status,
            "currentStage": workflow_status.get("current_stage", "unknown"),
            "progressPercentage": workflow_status.get("progress_percentage", 0.0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trace status: {str(e)}")

@router.delete("/{trace_id}")
async def delete_trace(
    trace_id: str,
    current_user: dict = Depends(require_permissions(["delete"]))
):
    """Delete a trace"""
    try:
        if trace_id not in TRACE_STORE:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        trace = TRACE_STORE[trace_id]
        
        # Check if user has access to this trace
        if trace.get("createdBy") != current_user["email"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Remove from store
        del TRACE_STORE[trace_id]
        
        return {"status": "success", "message": "Trace deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete trace: {str(e)}")

@router.get("/stats/summary")
async def get_trace_stats(current_user: dict = Depends(get_current_user)):
    """Get trace statistics"""
    try:
        # Filter traces by user
        user_traces = [
            trace for trace in TRACE_STORE.values()
            if trace.get("createdBy") == current_user["email"]
        ]
        
        total_traces = len(user_traces)
        completed_traces = len([t for t in user_traces if t["status"] == "completed"])
        failed_traces = len([t for t in user_traces if t["status"] == "failed"])
        running_traces = len([t for t in user_traces if t["status"] in ["running", "processing"]])
        
        # Calculate average confidence
        confidences = [t.get("overallConfidence", 0.0) for t in user_traces if t.get("overallConfidence")]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Calculate average duration
        durations = [t.get("totalDuration", 0) for t in user_traces if t.get("totalDuration")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Calculate total steps
        total_steps = sum(len(t.get("steps", [])) for t in user_traces)
        
        return {
            "total_traces": total_traces,
            "completed_traces": completed_traces,
            "failed_traces": failed_traces,
            "running_traces": running_traces,
            "average_confidence": avg_confidence,
            "average_duration_ms": avg_duration,
            "total_steps": total_steps,
            "success_rate": (completed_traces / total_traces * 100) if total_traces > 0 else 0.0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trace statistics: {str(e)}")

@router.get("/live/status")
async def get_live_trace_status(current_user: dict = Depends(get_current_user)):
    """Get live status of all running traces"""
    try:
        # Filter running traces by user
        running_traces = [
            trace for trace in TRACE_STORE.values()
            if trace.get("createdBy") == current_user["email"] and 
            trace["status"] in ["running", "processing"]
        ]
        
        # Get agent service for workflow status
        agent_service = AgentService()
        workflow_status = agent_service.get_workflow_status()
        
        live_status = []
        for trace in running_traces:
            live_status.append({
                "traceId": trace["traceId"],
                "goal": trace["goal"],
                "status": trace["status"],
                "startTime": trace["startTime"],
                "currentStage": workflow_status.get("current_stage", "unknown"),
                "progressPercentage": workflow_status.get("progress_percentage", 0.0),
                "completedStages": workflow_status.get("completed_stages", []),
                "failedStages": workflow_status.get("failed_stages", [])
            })
        
        return {
            "running_traces": live_status,
            "workflow_status": workflow_status,
            "last_update": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get live status: {str(e)}")
