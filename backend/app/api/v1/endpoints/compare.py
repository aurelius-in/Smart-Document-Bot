import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...services.agent_service import AgentService
from ...models.base import Document, DocumentType

router = APIRouter()

class ComparisonRequest(BaseModel):
    """Document comparison request model"""
    documentAId: str
    documentBId: str
    comparisonType: str = "semantic"

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

# Mock comparison storage
COMPARISON_STORE = {}

@router.post("/documents", response_model=ComparisonResult)
async def compare_documents(
    request: ComparisonRequest,
    current_user: dict = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Compare two documents"""
    try:
        # Import document store from documents endpoint
        from .documents import DOCUMENT_STORE
        
        # Validate documents exist
        if request.documentAId not in DOCUMENT_STORE:
            raise HTTPException(status_code=404, detail=f"Document A with ID {request.documentAId} not found")
        
        if request.documentBId not in DOCUMENT_STORE:
            raise HTTPException(status_code=404, detail=f"Document B with ID {request.documentBId} not found")
        
        # Get documents
        doc_a_data = DOCUMENT_STORE[request.documentAId]
        doc_b_data = DOCUMENT_STORE[request.documentBId]
        
        document_a = doc_a_data["document"]
        document_b = doc_b_data["document"]
        
        # Ensure documents have content
        if not document_a.content:
            raise HTTPException(status_code=400, detail="Document A has no content. Please process it first.")
        
        if not document_b.content:
            raise HTTPException(status_code=400, detail="Document B has no content. Please process it first.")
        
        # Generate comparison ID
        comparison_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Create initial comparison record
        comparison_record = {
            "id": comparison_id,
            "documentAId": request.documentAId,
            "documentBId": request.documentBId,
            "comparisonType": request.comparisonType,
            "status": "processing",
            "createdAt": start_time.isoformat(),
            "createdBy": current_user["email"]
        }
        
        COMPARISON_STORE[comparison_id] = comparison_record
        
        # Execute comparison using agent service
        comparison_result = await agent_service.compare_documents(
            document_a=document_a,
            document_b=document_b,
            goal=f"Compare documents for {request.comparisonType} differences and risk changes"
        )
        
        # Calculate duration
        end_time = datetime.utcnow()
        duration = int((end_time - start_time).total_seconds() * 1000)
        
        # Update comparison record
        if comparison_result["status"] == "completed":
            result_data = comparison_result["result"]
            
            # Extract comparison details
            semantic_diffs = []
            risk_delta = {}
            compliance_impact = {}
            
            if result_data and "comparison_results" in result_data:
                results = result_data["comparison_results"]
                
                # Extract semantic differences
                if "semantic" in results:
                    semantic_result = results["semantic"]
                    semantic_diffs = semantic_result.get("semantic_differences", [])
                
                # Extract risk delta
                if "compliance" in results:
                    compliance_result = results["compliance"]
                    risk_delta = {
                        "risk_delta": compliance_result.get("risk_delta", "No risk change detected"),
                        "compliance_impact": compliance_result.get("compliance_impact", "No compliance impact detected")
                    }
                
                # Extract compliance impact
                if "summary" in results:
                    summary = results["summary"]
                    compliance_impact = {
                        "overall_similarity": summary.get("overall_similarity", 0.0),
                        "total_differences": summary.get("total_differences", 0),
                        "insights": summary.get("insights", []),
                        "recommendations": summary.get("recommendations", [])
                    }
            
            comparison_record.update({
                "status": "completed",
                "semanticDiffs": semantic_diffs,
                "riskDelta": risk_delta,
                "complianceImpact": compliance_impact,
                "confidence": comparison_result.get("confidence", 0.0),
                "duration": duration,
                "result": comparison_result["result"]
            })
        else:
            comparison_record.update({
                "status": "failed",
                "error": comparison_result.get("error", "Comparison failed"),
                "confidence": 0.0,
                "duration": duration
            })
        
        return ComparisonResult(
            id=comparison_id,
            documentAId=request.documentAId,
            documentBId=request.documentBId,
            comparisonType=request.comparisonType,
            status=comparison_record["status"],
            semanticDiffs=comparison_record.get("semanticDiffs", []),
            riskDelta=comparison_record.get("riskDelta", {}),
            complianceImpact=comparison_record.get("complianceImpact", {}),
            confidence=comparison_record.get("confidence", 0.0),
            duration=comparison_record.get("duration", 0),
            createdAt=comparison_record["createdAt"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

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
        
        return ComparisonResult(
            id=comparison["id"],
            documentAId=comparison["documentAId"],
            documentBId=comparison["documentBId"],
            comparisonType=comparison["comparisonType"],
            status=comparison["status"],
            semanticDiffs=comparison.get("semanticDiffs", []),
            riskDelta=comparison.get("riskDelta", {}),
            complianceImpact=comparison.get("complianceImpact", {}),
            confidence=comparison.get("confidence", 0.0),
            duration=comparison.get("duration", 0),
            createdAt=comparison["createdAt"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve comparison: {str(e)}")

@router.get("/history", response_model=PaginatedResponse)
async def get_comparison_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get comparison history for the user"""
    try:
        # Filter comparisons by user
        user_comparisons = [
            comp for comp in COMPARISON_STORE.values()
            if comp.get("createdBy") == current_user["email"]
        ]
        
        # Calculate pagination
        total = len(user_comparisons)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # Get page of comparisons
        page_comparisons = user_comparisons[start_idx:end_idx]
        
        # Convert to ComparisonResult
        comparison_results = []
        for comparison in page_comparisons:
            comparison_result = ComparisonResult(
                id=comparison["id"],
                documentAId=comparison["documentAId"],
                documentBId=comparison["documentBId"],
                comparisonType=comparison["comparisonType"],
                status=comparison["status"],
                semanticDiffs=comparison.get("semanticDiffs", []),
                riskDelta=comparison.get("riskDelta", {}),
                complianceImpact=comparison.get("complianceImpact", {}),
                confidence=comparison.get("confidence", 0.0),
                duration=comparison.get("duration", 0),
                createdAt=comparison["createdAt"]
            )
            comparison_results.append(comparison_result)
        
        return PaginatedResponse(
            data=comparison_results,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve comparison history: {str(e)}")

@router.post("/content")
async def compare_content(
    content_a: str,
    content_b: str,
    comparison_type: str = "semantic",
    current_user: dict = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Compare raw content strings"""
    try:
        # Create temporary document objects
        document_a = Document(
            id="temp_a",
            filename="content_a.txt",
            content=content_a,
            doc_type=DocumentType.UNKNOWN,
            metadata={"source": "direct_content"}
        )
        
        document_b = Document(
            id="temp_b",
            filename="content_b.txt",
            content=content_b,
            doc_type=DocumentType.UNKNOWN,
            metadata={"source": "direct_content"}
        )
        
        # Execute comparison
        comparison_result = await agent_service.compare_documents(
            document_a=document_a,
            document_b=document_b,
            goal=f"Compare content for {comparison_type} differences"
        )
        
        return {
            "status": comparison_result["status"],
            "result": comparison_result["result"],
            "confidence": comparison_result.get("confidence", 0.0),
            "rationale": comparison_result.get("rationale", "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content comparison failed: {str(e)}")

@router.get("/stats/summary")
async def get_comparison_stats(current_user: dict = Depends(get_current_user)):
    """Get comparison statistics"""
    try:
        # Filter comparisons by user
        user_comparisons = [
            comp for comp in COMPARISON_STORE.values()
            if comp.get("createdBy") == current_user["email"]
        ]
        
        total_comparisons = len(user_comparisons)
        completed_comparisons = len([c for c in user_comparisons if c["status"] == "completed"])
        failed_comparisons = len([c for c in user_comparisons if c["status"] == "failed"])
        
        # Calculate average confidence
        confidences = [c.get("confidence", 0.0) for c in user_comparisons if c.get("confidence")]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Calculate average duration
        durations = [c.get("duration", 0) for c in user_comparisons if c.get("duration")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_comparisons": total_comparisons,
            "completed_comparisons": completed_comparisons,
            "failed_comparisons": failed_comparisons,
            "average_confidence": avg_confidence,
            "average_duration_ms": avg_duration,
            "success_rate": (completed_comparisons / total_comparisons * 100) if total_comparisons > 0 else 0.0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comparison statistics: {str(e)}")
