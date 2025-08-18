from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, Any, List, Optional
import logging

from ....services.agent_service import get_agent_service
from ....models.base import Document
from ....core.config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

@router.post("/summarize")
async def summarize_document(
    summary_type: str = "abstractive",
    summary_length: str = "medium",
    summary_style: str = "informative",
    target_audience: str = "general",
    focus_areas: Optional[List[str]] = None,
    business_context: Optional[str] = None,
    technical_domain: Optional[str] = None,
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Generate document summary using the SummarizerAgent"""
    try:
        # Prepare agent parameters based on summary type
        agent_params = {
            "summary_type": summary_type,
            "summary_length": summary_length,
            "summary_style": summary_style,
            "target_audience": target_audience
        }
        
        if focus_areas:
            agent_params["focus_areas"] = focus_areas
        if business_context:
            agent_params["business_context"] = business_context
        if technical_domain:
            agent_params["technical_domain"] = technical_domain
        
        # Execute summarizer agent
        result = await agent_service.execute_single_agent(
            agent_type="summarizer",
            document=document,
            goal=f"Generate {summary_type} summary"
        )
        
        return {
            "status": "success",
            "summary_type": summary_type,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in summarization: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@router.post("/extractive-summary")
async def extractive_summary(
    summary_length: str = "medium",
    focus_areas: Optional[List[str]] = None,
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Generate extractive summary by selecting key sentences"""
    try:
        agent_params = {
            "summary_type": "extractive",
            "summary_length": summary_length
        }
        
        if focus_areas:
            agent_params["focus_areas"] = focus_areas
        
        result = await agent_service.execute_single_agent(
            agent_type="summarizer",
            document=document,
            goal="Generate extractive summary"
        )
        
        return {
            "status": "success",
            "summary_type": "extractive",
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in extractive summarization: {e}")
        raise HTTPException(status_code=500, detail=f"Extractive summarization failed: {str(e)}")

@router.post("/executive-summary")
async def executive_summary(
    business_context: str = "general",
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Generate executive summary for business decision makers"""
    try:
        agent_params = {
            "summary_type": "executive",
            "business_context": business_context
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="summarizer",
            document=document,
            goal="Generate executive summary"
        )
        
        return {
            "status": "success",
            "summary_type": "executive",
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in executive summarization: {e}")
        raise HTTPException(status_code=500, detail=f"Executive summarization failed: {str(e)}")

@router.post("/technical-summary")
async def technical_summary(
    technical_domain: str = "general",
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Generate technical summary for subject matter experts"""
    try:
        agent_params = {
            "summary_type": "technical",
            "technical_domain": technical_domain
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="summarizer",
            document=document,
            goal="Generate technical summary"
        )
        
        return {
            "status": "success",
            "summary_type": "technical",
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in technical summarization: {e}")
        raise HTTPException(status_code=500, detail=f"Technical summarization failed: {str(e)}")

@router.post("/key-points")
async def extract_key_points(
    point_categories: Optional[List[str]] = None,
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Extract key points organized by categories"""
    try:
        if not point_categories:
            point_categories = ["main_points", "key_facts", "important_dates", "critical_issues"]
        
        agent_params = {
            "point_categories": point_categories
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="summarizer",
            document=document,
            goal="Extract key points by categories"
        )
        
        return {
            "status": "success",
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in key points extraction: {e}")
        raise HTTPException(status_code=500, detail=f"Key points extraction failed: {str(e)}")

@router.post("/summary-comparison")
async def compare_summaries(
    summary_a: str,
    summary_b: str,
    comparison_criteria: Optional[List[str]] = None,
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Compare two summaries and identify differences"""
    try:
        if not comparison_criteria:
            comparison_criteria = ["completeness", "accuracy", "clarity", "coverage"]
        
        # Create a mock document with the comparison data
        comparison_doc = Document(
            id=0,
            filename="comparison",
            content=f"Summary A: {summary_a}\n\nSummary B: {summary_b}",
            file_path="",
            file_size=0,
            content_type="text/plain"
        )
        
        agent_params = {
            "comparison_criteria": comparison_criteria
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="summarizer",
            document=comparison_doc,
            goal="Compare summaries"
        )
        
        return {
            "status": "success",
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in summary comparison: {e}")
        raise HTTPException(status_code=500, detail=f"Summary comparison failed: {str(e)}")

@router.post("/summary-validation")
async def validate_summary(
    summary: str,
    original_content: str,
    validation_criteria: Optional[List[str]] = None,
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Validate summary accuracy and completeness"""
    try:
        if not validation_criteria:
            validation_criteria = ["factual_accuracy", "completeness", "coherence", "relevance"]
        
        # Create a mock document with the validation data
        validation_doc = Document(
            id=0,
            filename="validation",
            content=f"Original: {original_content}\n\nSummary: {summary}",
            file_path="",
            file_size=0,
            content_type="text/plain"
        )
        
        agent_params = {
            "validation_criteria": validation_criteria
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="summarizer",
            document=validation_doc,
            goal="Validate summary"
        )
        
        return {
            "status": "success",
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in summary validation: {e}")
        raise HTTPException(status_code=500, detail=f"Summary validation failed: {str(e)}")

@router.get("/capabilities")
async def get_summarizer_capabilities() -> Dict[str, Any]:
    """Get available summarizer capabilities"""
    return {
        "summary_types": [
            "abstractive",
            "extractive", 
            "executive",
            "technical"
        ],
        "summary_lengths": [
            "short",
            "medium",
            "long"
        ],
        "summary_styles": [
            "informative",
            "narrative",
            "analytical",
            "technical"
        ],
        "target_audiences": [
            "general",
            "professional",
            "technical",
            "executive"
        ],
        "business_contexts": [
            "general",
            "financial",
            "legal",
            "operational",
            "strategic"
        ],
        "technical_domains": [
            "general",
            "software",
            "engineering",
            "scientific",
            "medical"
        ],
        "features": [
            "extractive_summary",
            "abstractive_summary", 
            "executive_summary",
            "technical_summary",
            "key_points_extraction",
            "summary_comparison",
            "summary_validation"
        ]
    }
