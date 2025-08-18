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

class SummarizationRequest(BaseModel):
    document_content: str
    summary_type: str = "abstractive"  # extractive, abstractive, executive, technical
    summary_length: str = "medium"  # short, medium, long
    summary_style: str = "informative"  # informative, narrative, analytical, technical
    target_audience: str = "general"  # general, professional, technical, executive
    focus_areas: Optional[List[str]] = None
    business_context: Optional[str] = "general"
    technical_domain: Optional[str] = "general"

class ExtractiveSummaryRequest(BaseModel):
    document_content: str
    summary_length: str = "medium"
    focus_areas: Optional[List[str]] = None

class ExecutiveSummaryRequest(BaseModel):
    document_content: str
    business_context: str = "general"

class TechnicalSummaryRequest(BaseModel):
    document_content: str
    technical_domain: str = "general"

class KeyPointsRequest(BaseModel):
    document_content: str
    point_categories: Optional[List[str]] = None

class SummaryComparisonRequest(BaseModel):
    summary_a: str
    summary_b: str
    comparison_criteria: Optional[List[str]] = None

class SummaryValidationRequest(BaseModel):
    summary: str
    original_content: str
    validation_criteria: Optional[List[str]] = None

@router.post("/summarize")
async def summarize_document(
    request: SummarizationRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Generate a summary of the document based on the specified type"""
    
    try:
        with monitor.agent_execution("summarizer", "summarize_document"):
            result = await agent_service.execute_single_agent(
                agent_type="summarizer",
                document_content=request.document_content,
                goal=f"Generate {request.summary_type} summary",
                summary_type=request.summary_type,
                summary_length=request.summary_length,
                summary_style=request.summary_style,
                target_audience=request.target_audience,
                focus_areas=request.focus_areas,
                business_context=request.business_context,
                technical_domain=request.technical_domain
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="summarizer",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "summary": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in document summarization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@router.post("/extractive")
async def extractive_summary(
    request: ExtractiveSummaryRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Generate an extractive summary by selecting key sentences"""
    
    try:
        with monitor.agent_execution("summarizer", "extractive_summary"):
            result = await agent_service.execute_single_agent(
                agent_type="summarizer",
                document_content=request.document_content,
                goal="Generate extractive summary",
                summary_type="extractive",
                summary_length=request.summary_length,
                focus_areas=request.focus_areas
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="summarizer",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "extractive_summary": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in extractive summarization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extractive summarization failed: {str(e)}")

@router.post("/executive")
async def executive_summary(
    request: ExecutiveSummaryRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Generate an executive summary for business decision makers"""
    
    try:
        with monitor.agent_execution("summarizer", "executive_summary"):
            result = await agent_service.execute_single_agent(
                agent_type="summarizer",
                document_content=request.document_content,
                goal="Generate executive summary",
                summary_type="executive",
                business_context=request.business_context
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="summarizer",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "executive_summary": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in executive summarization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Executive summarization failed: {str(e)}")

@router.post("/technical")
async def technical_summary(
    request: TechnicalSummaryRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Generate a technical summary for subject matter experts"""
    
    try:
        with monitor.agent_execution("summarizer", "technical_summary"):
            result = await agent_service.execute_single_agent(
                agent_type="summarizer",
                document_content=request.document_content,
                goal="Generate technical summary",
                summary_type="technical",
                technical_domain=request.technical_domain
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="summarizer",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "technical_summary": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in technical summarization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Technical summarization failed: {str(e)}")

@router.post("/key-points")
async def extract_key_points(
    request: KeyPointsRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Extract key points organized by categories"""
    
    try:
        with monitor.agent_execution("summarizer", "key_points_extraction"):
            result = await agent_service.execute_single_agent(
                agent_type="summarizer",
                document_content=request.document_content,
                goal="Extract key points",
                point_categories=request.point_categories
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="summarizer",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "key_points": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in key points extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Key points extraction failed: {str(e)}")

@router.post("/compare")
async def compare_summaries(
    request: SummaryComparisonRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Compare two summaries and identify differences"""
    
    try:
        with monitor.agent_execution("summarizer", "summary_comparison"):
            result = await agent_service.execute_single_agent(
                agent_type="summarizer",
                document_content=f"Summary A: {request.summary_a}\n\nSummary B: {request.summary_b}",
                goal="Compare summaries",
                comparison_criteria=request.comparison_criteria
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="summarizer",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "comparison": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in summary comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summary comparison failed: {str(e)}")

@router.post("/validate")
async def validate_summary(
    request: SummaryValidationRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Validate summary accuracy and completeness"""
    
    try:
        with monitor.agent_execution("summarizer", "summary_validation"):
            result = await agent_service.execute_single_agent(
                agent_type="summarizer",
                document_content=f"Original: {request.original_content}\n\nSummary: {request.summary}",
                goal="Validate summary",
                validation_criteria=request.validation_criteria
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="summarizer",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "validation": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in summary validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summary validation failed: {str(e)}")

@router.get("/types")
async def get_summary_types():
    """Get available summary types and their descriptions"""
    
    summary_types = {
        "extractive": {
            "description": "Selects key sentences from the original text",
            "use_cases": ["Quick overview", "Fact extraction", "Key information retrieval"],
            "parameters": ["summary_length", "focus_areas"]
        },
        "abstractive": {
            "description": "Creates new text that captures the essence",
            "use_cases": ["Comprehensive understanding", "Creative summarization", "Content generation"],
            "parameters": ["summary_style", "target_audience"]
        },
        "executive": {
            "description": "High-level summary for business decision makers",
            "use_cases": ["Business reports", "Strategic planning", "Executive briefings"],
            "parameters": ["business_context"]
        },
        "technical": {
            "description": "Detailed technical summary for subject matter experts",
            "use_cases": ["Technical documentation", "Research papers", "Engineering reports"],
            "parameters": ["technical_domain"]
        }
    }
    
    return {
        "success": True,
        "summary_types": summary_types
    }
