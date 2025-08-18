from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...services.agent_service import AgentService

router = APIRouter()


class ComparisonRequest(BaseModel):
    """Document comparison request model"""
    documentAId: str
    documentBId: str
    comparisonType: str = "semantic"  # semantic, structural, compliance, risk


class ComparisonResult(BaseModel):
    """Document comparison result model"""
    id: str
    documentAId: str
    documentBId: str
    comparisonType: str
    status: str
    semanticDiffs: List[dict] = []
    riskDelta: dict = {}
    complianceImpact: dict = {}
    confidence: float
    duration: int
    createdAt: str


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[ComparisonResult]
    pagination: dict


# Mock comparison storage - in production, this would be a database
COMPARISON_STORE = {}


@router.post("/documents", response_model=ComparisonResult)
async def compare_documents(
    request: ComparisonRequest,
    current_user: dict = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Compare two documents"""
    try:
        # Generate comparison ID
        comparison_id = f"comp_{request.documentAId}_{request.documentBId}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create initial comparison record
        comparison_result = {
            "id": comparison_id,
            "documentAId": request.documentAId,
            "documentBId": request.documentBId,
            "comparisonType": request.comparisonType,
            "status": "processing",
            "semanticDiffs": [],
            "riskDelta": {},
            "complianceImpact": {},
            "confidence": 0.0,
            "duration": 0,
            "createdAt": datetime.utcnow().isoformat()
        }
        
        # Store comparison record
        COMPARISON_STORE[comparison_id] = comparison_result
        
        # In a real implementation, this would fetch documents from database
        # For demo purposes, we'll use sample content
        doc_a_content = f"Sample content for document {request.documentAId}"
        doc_b_content = f"Sample content for document {request.documentBId}"
        
        # Create temporary documents for comparison
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f_a:
            f_a.write(doc_a_content)
            doc_a_path = f_a.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f_b:
            f_b.write(doc_b_content)
            doc_b_path = f_b.name
        
        try:
            # Compare documents
            result = await agent_service.compare_documents(doc_a_path, doc_b_path)
            
            # Update comparison result
            comparison_result.update({
                "status": "completed",
                "semanticDiffs": result.get("result", {}).get("semantic_diffs", []),
                "riskDelta": result.get("result", {}).get("risk_delta", {}),
                "complianceImpact": result.get("result", {}).get("compliance_impact", {}),
                "confidence": result.get("confidence", 0.0),
                "duration": result.get("duration_ms", 0)
            })
            
            return ComparisonResult(**comparison_result)
            
        finally:
            # Clean up temporary files
            os.unlink(doc_a_path)
            os.unlink(doc_b_path)
        
    except Exception as e:
        # Update status to error
        if comparison_id in COMPARISON_STORE:
            COMPARISON_STORE[comparison_id]["status"] = "error"
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{comparison_id}", response_model=ComparisonResult)
async def get_comparison_result(
    comparison_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific comparison result"""
    try:
        if comparison_id not in COMPARISON_STORE:
            raise HTTPException(status_code=404, detail="Comparison not found")
        
        comparison = COMPARISON_STORE[comparison_id]
        return ComparisonResult(**comparison)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=PaginatedResponse)
async def get_comparison_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get comparison history for the user"""
    try:
        # Get all comparisons
        comparisons = list(COMPARISON_STORE.values())
        
        # Calculate pagination
        total = len(comparisons)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_comparisons = comparisons[start_idx:end_idx]
        
        # Convert to ComparisonResult models
        comparison_results = [
            ComparisonResult(**comp) for comp in paginated_comparisons
        ]
        
        return PaginatedResponse(
            data=comparison_results,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content")
async def compare_content(
    content_a: str,
    content_b: str,
    comparison_type: str = "semantic",
    current_user: dict = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Compare document content directly"""
    try:
        # Create temporary files for comparison
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f_a:
            f_a.write(content_a)
            doc_a_path = f_a.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f_b:
            f_b.write(content_b)
            doc_b_path = f_b.name
        
        try:
            # Compare documents
            result = await agent_service.compare_documents(doc_a_path, doc_b_path)
            
            return {
                "comparison_type": comparison_type,
                "semantic_diffs": result.get("result", {}).get("semantic_diffs", []),
                "risk_delta": result.get("result", {}).get("risk_delta", {}),
                "compliance_impact": result.get("result", {}).get("compliance_impact", {}),
                "confidence": result.get("confidence", 0.0),
                "duration_ms": result.get("duration_ms", 0)
            }
            
        finally:
            # Clean up temporary files
            os.unlink(doc_a_path)
            os.unlink(doc_b_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_comparison_stats(current_user: dict = Depends(get_current_user)):
    """Get comparison statistics"""
    try:
        comparisons = list(COMPARISON_STORE.values())
        
        total_comparisons = len(comparisons)
        completed_comparisons = len([c for c in comparisons if c["status"] == "completed"])
        error_comparisons = len([c for c in comparisons if c["status"] == "error"])
        
        avg_confidence = 0.0
        if completed_comparisons > 0:
            avg_confidence = sum(c.get("confidence", 0) for c in comparisons if c["status"] == "completed") / completed_comparisons
        
        avg_duration = 0.0
        if completed_comparisons > 0:
            avg_duration = sum(c.get("duration", 0) for c in comparisons if c["status"] == "completed") / completed_comparisons
        
        return {
            "total_comparisons": total_comparisons,
            "completed_comparisons": completed_comparisons,
            "error_comparisons": error_comparisons,
            "average_confidence": avg_confidence,
            "average_duration_ms": avg_duration,
            "success_rate": (completed_comparisons / total_comparisons * 100) if total_comparisons > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
