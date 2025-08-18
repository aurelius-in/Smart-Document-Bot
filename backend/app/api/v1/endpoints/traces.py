from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from ...core.security import get_current_user, require_permissions
from ...services.agent_service import AgentService

router = APIRouter()


@router.get("/{trace_id}")
async def get_trace(
    trace_id: str,
    current_user: str = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """Get a specific trace by ID"""
    try:
        trace = await agent_service.get_trace(trace_id)
        if not trace:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        return trace
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_traces(
    current_user: str = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """List all traces"""
    try:
        traces = await agent_service.get_all_traces()
        return {"traces": traces}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trace_id}/updates")
async def get_trace_updates(
    trace_id: str,
    current_user: str = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """Get latest updates for a trace"""
    try:
        updates = await agent_service.get_trace_updates(trace_id)
        if not updates:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        return updates
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trace_id}/status")
async def get_trace_status(
    trace_id: str,
    current_user: str = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """Get trace status"""
    try:
        is_complete = await agent_service.is_trace_complete(trace_id)
        return {
            "trace_id": trace_id,
            "is_complete": is_complete,
            "status": "completed" if is_complete else "running"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{trace_id}")
async def delete_trace(
    trace_id: str,
    current_user: str = Depends(require_permissions(["delete"])),
    agent_service: AgentService = Depends()
):
    """Delete a trace (admin only)"""
    try:
        # In a real implementation, this would delete from database
        # For now, just return success
        return {"message": "Trace deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
