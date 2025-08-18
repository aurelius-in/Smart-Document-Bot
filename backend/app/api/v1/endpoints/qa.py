from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...services.agent_service import AgentService

router = APIRouter()


class QARequest(BaseModel):
    """Q&A request model"""
    question: str
    document_content: Optional[str] = None
    document_id: Optional[str] = None
    context: Optional[dict] = {}


class QAResponse(BaseModel):
    """Q&A response model"""
    answer: str
    confidence: float
    citations: List[dict] = []
    sources: List[str] = []
    duration_ms: int


@router.post("/ask", response_model=QAResponse)
async def ask_question(
    request: QARequest,
    current_user: str = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Ask a question about a document"""
    try:
        # Get document content if document_id is provided
        document_content = request.document_content
        if request.document_id and not document_content:
            # In a real implementation, this would fetch from database
            document_content = "Sample document content for demo purposes"
        
        if not document_content:
            raise HTTPException(
                status_code=400,
                detail="Either document_content or document_id must be provided"
            )
        
        # Answer question
        result = await agent_service.answer_question(
            question=request.question,
            document_content=document_content
        )
        
        return QAResponse(
            answer=result["result"].answer,
            confidence=result["confidence"],
            citations=result["result"].citations,
            sources=result["result"].sources,
            duration_ms=result["duration_ms"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_questions(
    questions: List[QARequest],
    current_user: str = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Ask multiple questions in batch"""
    try:
        results = []
        for question_request in questions:
            try:
                result = await agent_service.answer_question(
                    question=question_request.question,
                    document_content=question_request.document_content or "Sample content"
                )
                
                results.append({
                    "question": question_request.question,
                    "answer": result["result"].answer,
                    "confidence": result["confidence"],
                    "citations": result["result"].citations,
                    "duration_ms": result["duration_ms"]
                })
                
            except Exception as e:
                results.append({
                    "question": question_request.question,
                    "error": str(e),
                    "confidence": 0.0
                })
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_question_suggestions(
    document_type: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Get suggested questions based on document type"""
    suggestions = {
        "contract": [
            "What are the key terms and conditions?",
            "Who are the parties involved?",
            "What are the payment terms?",
            "What are the termination conditions?",
            "What are the liability clauses?"
        ],
        "policy": [
            "What is the coverage scope?",
            "What are the exclusions?",
            "What are the premium amounts?",
            "What are the claim procedures?",
            "What are the renewal terms?"
        ],
        "regulation": [
            "What are the compliance requirements?",
            "What are the penalties for violations?",
            "What are the reporting obligations?",
            "What are the effective dates?",
            "What are the enforcement mechanisms?"
        ],
        "general": [
            "What is the main purpose of this document?",
            "What are the key dates mentioned?",
            "What are the important obligations?",
            "What are the risk factors?",
            "What are the compliance implications?"
        ]
    }
    
    if document_type and document_type in suggestions:
        return {"suggestions": suggestions[document_type]}
    else:
        return {"suggestions": suggestions["general"]}
