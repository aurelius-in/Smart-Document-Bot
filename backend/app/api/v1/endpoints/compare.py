from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...services.agent_service import AgentService

router = APIRouter()


class CompareRequest(BaseModel):
    """Document comparison request model"""
    document_a_id: str
    document_b_id: str
    comparison_type: str = "semantic"  # semantic, risk, compliance
    context: Optional[dict] = {}


class CompareResponse(BaseModel):
    """Document comparison response model"""
    comparison_id: str
    document_a_id: str
    document_b_id: str
    semantic_diffs: List[dict] = []
    risk_delta: dict = {}
    compliance_impact: dict = {}
    confidence: float
    duration_ms: int


@router.post("/documents", response_model=CompareResponse)
async def compare_documents(
    request: CompareRequest,
    current_user: str = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Compare two documents"""
    try:
        # In a real implementation, this would fetch documents from database
        # For demo purposes, we'll use sample content
        doc_a_content = f"Sample content for document {request.document_a_id}"
        doc_b_content = f"Sample content for document {request.document_b_id}"
        
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
            
            return CompareResponse(
                comparison_id=f"comp_{request.document_a_id}_{request.document_b_id}",
                document_a_id=request.document_a_id,
                document_b_id=request.document_b_id,
                semantic_diffs=result.get("result", {}).get("semantic_diffs", []),
                risk_delta=result.get("result", {}).get("risk_delta", {}),
                compliance_impact=result.get("result", {}).get("compliance_impact", {}),
                confidence=result.get("confidence", 0.0),
                duration_ms=result.get("duration_ms", 0)
            )
            
        finally:
            # Clean up temporary files
            os.unlink(doc_a_path)
            os.unlink(doc_b_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content")
async def compare_content(
    content_a: str,
    content_b: str,
    comparison_type: str = "semantic",
    current_user: str = Depends(require_permissions(["analyze"])),
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


@router.get("/history")
async def get_comparison_history(
    current_user: str = Depends(get_current_user)
):
    """Get comparison history for the user"""
    # In a real implementation, this would fetch from database
    return {
        "comparisons": [
            {
                "comparison_id": "comp_123_456",
                "document_a_id": "123",
                "document_b_id": "456",
                "comparison_type": "semantic",
                "created_at": "2024-01-01T00:00:00Z",
                "confidence": 0.85
            }
        ]
    }


@router.get("/{comparison_id}")
async def get_comparison_result(
    comparison_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific comparison result"""
    # In a real implementation, this would fetch from database
    return {
        "comparison_id": comparison_id,
        "document_a_id": "123",
        "document_b_id": "456",
        "semantic_diffs": [
            {
                "section": "parties",
                "differences": [
                    {
                        "type": "modified",
                        "description": "Company name changed",
                        "doc_a_value": "Old Company Inc.",
                        "doc_b_value": "New Company LLC",
                        "impact": "medium"
                    }
                ]
            }
        ],
        "risk_delta": {
            "overall": 0.15,
            "liability": 0.2,
            "compliance": -0.1
        },
        "compliance_impact": {
            "level": "medium",
            "actions_required": ["Update registration", "Notify regulators"]
        },
        "confidence": 0.85,
        "created_at": "2024-01-01T00:00:00Z"
    }
