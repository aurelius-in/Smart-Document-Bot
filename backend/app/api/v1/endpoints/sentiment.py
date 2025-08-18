from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, Any, List, Optional
import logging

from ....services.agent_service import get_agent_service
from ....models.base import Document
from ....core.config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

@router.post("/analyze-sentiment")
async def analyze_sentiment(
    analysis_depth: str = "comprehensive",
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Analyze overall sentiment of the document"""
    try:
        agent_params = {
            "analysis_depth": analysis_depth
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="sentiment",
            document=document,
            goal="Analyze sentiment"
        )
        
        return {
            "status": "success",
            "analysis_depth": analysis_depth,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.post("/analyze-tone")
async def analyze_tone(
    tone_categories: Optional[List[str]] = None,
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Analyze the tone and writing style of the document"""
    try:
        if not tone_categories:
            tone_categories = ["formal", "informal", "professional", "casual", "authoritative", "friendly", "neutral"]
        
        agent_params = {
            "tone_categories": tone_categories
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="sentiment",
            document=document,
            goal="Analyze tone"
        )
        
        return {
            "status": "success",
            "tone_categories": tone_categories,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in tone analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Tone analysis failed: {str(e)}")

@router.post("/detect-emotions")
async def detect_emotions(
    emotion_categories: Optional[List[str]] = None,
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Detect specific emotions expressed in the document"""
    try:
        if not emotion_categories:
            emotion_categories = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation"]
        
        agent_params = {
            "emotion_categories": emotion_categories
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="sentiment",
            document=document,
            goal="Detect emotions"
        )
        
        return {
            "status": "success",
            "emotion_categories": emotion_categories,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in emotion detection: {e}")
        raise HTTPException(status_code=500, detail=f"Emotion detection failed: {str(e)}")

@router.post("/track-sentiment")
async def track_sentiment(
    tracking_granularity: str = "paragraph",
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Track sentiment changes throughout the document"""
    try:
        agent_params = {
            "tracking_granularity": tracking_granularity
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="sentiment",
            document=document,
            goal="Track sentiment changes"
        )
        
        return {
            "status": "success",
            "tracking_granularity": tracking_granularity,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment tracking: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment tracking failed: {str(e)}")

@router.post("/detect-bias")
async def detect_bias(
    bias_types: Optional[List[str]] = None,
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Detect various types of bias in the document"""
    try:
        if not bias_types:
            bias_types = ["cognitive", "confirmation", "anchoring", "availability", "gender", "racial", "political"]
        
        agent_params = {
            "bias_types": bias_types
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="sentiment",
            document=document,
            goal="Detect bias"
        )
        
        return {
            "status": "success",
            "bias_types": bias_types,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in bias detection: {e}")
        raise HTTPException(status_code=500, detail=f"Bias detection failed: {str(e)}")

@router.post("/context-sentiment")
async def context_sentiment(
    context_type: str = "general",
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Analyze sentiment in specific contexts"""
    try:
        agent_params = {
            "context_type": context_type
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="sentiment",
            document=document,
            goal=f"Analyze sentiment in {context_type} context"
        )
        
        return {
            "status": "success",
            "context_type": context_type,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in context sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Context sentiment analysis failed: {str(e)}")

@router.post("/compare-sentiment")
async def compare_sentiment(
    text_a: str,
    text_b: str,
    comparison_criteria: Optional[List[str]] = None,
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Compare sentiment between two texts"""
    try:
        if not comparison_criteria:
            comparison_criteria = ["overall_sentiment", "sentiment_intensity", "tone", "emotions"]
        
        # Create a mock document with the comparison data
        comparison_doc = Document(
            id=0,
            filename="sentiment_comparison",
            content=f"Text A: {text_a}\n\nText B: {text_b}",
            file_path="",
            file_size=0,
            content_type="text/plain"
        )
        
        agent_params = {
            "comparison_criteria": comparison_criteria
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="sentiment",
            document=comparison_doc,
            goal="Compare sentiment"
        )
        
        return {
            "status": "success",
            "comparison_criteria": comparison_criteria,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment comparison: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment comparison failed: {str(e)}")

@router.post("/validate-sentiment")
async def validate_sentiment(
    text: str,
    sentiment_analysis: Dict[str, Any],
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Validate sentiment analysis results"""
    try:
        # Create a mock document with the validation data
        validation_doc = Document(
            id=0,
            filename="sentiment_validation",
            content=f"Text: {text}\n\nAnalysis: {str(sentiment_analysis)}",
            file_path="",
            file_size=0,
            content_type="text/plain"
        )
        
        result = await agent_service.execute_single_agent(
            agent_type="sentiment",
            document=validation_doc,
            goal="Validate sentiment analysis"
        )
        
        return {
            "status": "success",
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment validation: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment validation failed: {str(e)}")

@router.get("/capabilities")
async def get_sentiment_capabilities() -> Dict[str, Any]:
    """Get available sentiment analysis capabilities"""
    return {
        "analysis_depths": [
            "basic",
            "detailed",
            "comprehensive"
        ],
        "tone_categories": [
            "formal",
            "informal",
            "professional",
            "casual",
            "authoritative",
            "friendly",
            "neutral",
            "emotional",
            "objective",
            "subjective",
            "confident",
            "uncertain",
            "respectful",
            "condescending"
        ],
        "emotion_categories": [
            "joy",
            "sadness",
            "anger",
            "fear",
            "surprise",
            "disgust",
            "trust",
            "anticipation"
        ],
        "tracking_granularities": [
            "sentence",
            "paragraph",
            "section",
            "overall"
        ],
        "bias_types": [
            "cognitive",
            "confirmation",
            "anchoring",
            "availability",
            "gender",
            "racial",
            "political",
            "cultural",
            "linguistic"
        ],
        "context_types": [
            "general",
            "business",
            "academic",
            "legal",
            "medical",
            "customer_service",
            "marketing"
        ],
        "comparison_criteria": [
            "overall_sentiment",
            "sentiment_intensity",
            "tone",
            "emotions",
            "bias",
            "context_appropriateness"
        ],
        "features": [
            "sentiment_analysis",
            "tone_analysis",
            "emotion_detection",
            "sentiment_tracking",
            "bias_detection",
            "context_sentiment",
            "sentiment_comparison",
            "sentiment_validation"
        ]
    }
