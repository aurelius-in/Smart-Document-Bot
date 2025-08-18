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

class SentimentAnalysisRequest(BaseModel):
    text: str
    analysis_depth: str = "comprehensive"  # basic, detailed, comprehensive

class ToneAnalysisRequest(BaseModel):
    text: str
    tone_categories: Optional[List[str]] = None

class EmotionDetectionRequest(BaseModel):
    text: str
    emotion_categories: Optional[List[str]] = None

class SentimentTrackingRequest(BaseModel):
    text: str
    tracking_granularity: str = "paragraph"  # sentence, paragraph, section, overall

class BiasDetectionRequest(BaseModel):
    text: str
    bias_types: Optional[List[str]] = None

class ContextSentimentRequest(BaseModel):
    text: str
    context_type: str = "general"  # general, business, academic, legal, medical, customer_service, marketing

class SentimentComparisonRequest(BaseModel):
    text_a: str
    text_b: str
    comparison_criteria: Optional[List[str]] = None

class SentimentValidationRequest(BaseModel):
    text: str
    sentiment_analysis: Dict[str, Any]

@router.post("/analyze")
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Analyze overall sentiment of the text"""
    
    try:
        with monitor.agent_execution("sentiment", "sentiment_analysis"):
            result = await agent_service.execute_single_agent(
                agent_type="sentiment",
                document_content=request.text,
                goal="Analyze sentiment",
                analysis_depth=request.analysis_depth
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="sentiment",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "sentiment_analysis": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.post("/tone")
async def analyze_tone(
    request: ToneAnalysisRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Analyze the tone and writing style of the text"""
    
    try:
        with monitor.agent_execution("sentiment", "tone_analysis"):
            result = await agent_service.execute_single_agent(
                agent_type="sentiment",
                document_content=request.text,
                goal="Analyze tone",
                tone_categories=request.tone_categories
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="sentiment",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "tone_analysis": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in tone analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tone analysis failed: {str(e)}")

@router.post("/emotions")
async def detect_emotions(
    request: EmotionDetectionRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Detect specific emotions expressed in the text"""
    
    try:
        with monitor.agent_execution("sentiment", "emotion_detection"):
            result = await agent_service.execute_single_agent(
                agent_type="sentiment",
                document_content=request.text,
                goal="Detect emotions",
                emotion_categories=request.emotion_categories
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="sentiment",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "emotion_detection": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in emotion detection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Emotion detection failed: {str(e)}")

@router.post("/tracking")
async def track_sentiment(
    request: SentimentTrackingRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Track sentiment changes throughout the text"""
    
    try:
        with monitor.agent_execution("sentiment", "sentiment_tracking"):
            result = await agent_service.execute_single_agent(
                agent_type="sentiment",
                document_content=request.text,
                goal="Track sentiment",
                tracking_granularity=request.tracking_granularity
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="sentiment",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "sentiment_tracking": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment tracking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sentiment tracking failed: {str(e)}")

@router.post("/bias")
async def detect_bias(
    request: BiasDetectionRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Detect various types of bias in the text"""
    
    try:
        with monitor.agent_execution("sentiment", "bias_detection"):
            result = await agent_service.execute_single_agent(
                agent_type="sentiment",
                document_content=request.text,
                goal="Detect bias",
                bias_types=request.bias_types
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="sentiment",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "bias_detection": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in bias detection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bias detection failed: {str(e)}")

@router.post("/context")
async def context_sentiment(
    request: ContextSentimentRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Analyze sentiment in specific contexts"""
    
    try:
        with monitor.agent_execution("sentiment", "context_sentiment"):
            result = await agent_service.execute_single_agent(
                agent_type="sentiment",
                document_content=request.text,
                goal="Context sentiment analysis",
                context_type=request.context_type
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="sentiment",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "context_sentiment": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in context sentiment analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Context sentiment analysis failed: {str(e)}")

@router.post("/compare")
async def compare_sentiment(
    request: SentimentComparisonRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Compare sentiment between two texts"""
    
    try:
        with monitor.agent_execution("sentiment", "sentiment_comparison"):
            result = await agent_service.execute_single_agent(
                agent_type="sentiment",
                document_content=f"Text A: {request.text_a}\n\nText B: {request.text_b}",
                goal="Compare sentiment",
                comparison_criteria=request.comparison_criteria
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="sentiment",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "sentiment_comparison": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sentiment comparison failed: {str(e)}")

@router.post("/validate")
async def validate_sentiment(
    request: SentimentValidationRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Validate sentiment analysis results"""
    
    try:
        with monitor.agent_execution("sentiment", "sentiment_validation"):
            result = await agent_service.execute_single_agent(
                agent_type="sentiment",
                document_content=request.text,
                goal="Validate sentiment analysis",
                sentiment_analysis=request.sentiment_analysis
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="sentiment",
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
        logger.error(f"Error in sentiment validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sentiment validation failed: {str(e)}")

@router.get("/analysis-depths")
async def get_analysis_depths():
    """Get available analysis depth levels"""
    
    analysis_depths = {
        "basic": {
            "description": "Simple positive/negative/neutral classification",
            "features": ["Basic sentiment polarity", "Quick analysis", "Low computational cost"]
        },
        "detailed": {
            "description": "Includes intensity and confidence scores",
            "features": ["Sentiment intensity", "Confidence scoring", "Detailed breakdown"]
        },
        "comprehensive": {
            "description": "Includes context, nuances, and detailed breakdown",
            "features": ["Contextual analysis", "Nuance detection", "Mixed sentiment analysis", "Key indicators"]
        }
    }
    
    return {
        "success": True,
        "analysis_depths": analysis_depths
    }

@router.get("/tone-categories")
async def get_tone_categories():
    """Get available tone categories"""
    
    tone_categories = {
        "formal": "Professional and business-appropriate",
        "informal": "Casual and conversational",
        "professional": "Business and industry-focused",
        "casual": "Relaxed and friendly",
        "authoritative": "Confident and commanding",
        "friendly": "Warm and approachable",
        "neutral": "Balanced and objective",
        "emotional": "Expressive and feeling-based",
        "objective": "Factual and unbiased",
        "subjective": "Personal and opinion-based",
        "confident": "Assured and certain",
        "uncertain": "Hesitant and doubtful",
        "respectful": "Polite and considerate",
        "condescending": "Patronizing and superior"
    }
    
    return {
        "success": True,
        "tone_categories": tone_categories
    }

@router.get("/emotion-categories")
async def get_emotion_categories():
    """Get available emotion categories (Plutchik's wheel)"""
    
    emotion_categories = {
        "joy": {
            "description": "Happiness, pleasure, contentment",
            "intensity_levels": ["serenity", "joy", "ecstasy"]
        },
        "sadness": {
            "description": "Grief, sorrow, melancholy",
            "intensity_levels": ["pensiveness", "sadness", "grief"]
        },
        "anger": {
            "description": "Rage, frustration, irritation",
            "intensity_levels": ["annoyance", "anger", "fury"]
        },
        "fear": {
            "description": "Anxiety, worry, terror",
            "intensity_levels": ["apprehension", "fear", "terror"]
        },
        "surprise": {
            "description": "Astonishment, amazement, shock",
            "intensity_levels": ["distraction", "surprise", "amazement"]
        },
        "disgust": {
            "description": "Aversion, repulsion, contempt",
            "intensity_levels": ["boredom", "disgust", "loathing"]
        },
        "trust": {
            "description": "Confidence, faith, acceptance",
            "intensity_levels": ["acceptance", "trust", "admiration"]
        },
        "anticipation": {
            "description": "Expectation, interest, vigilance",
            "intensity_levels": ["interest", "anticipation", "vigilance"]
        }
    }
    
    return {
        "success": True,
        "emotion_categories": emotion_categories
    }

@router.get("/bias-types")
async def get_bias_types():
    """Get available bias types for detection"""
    
    bias_types = {
        "cognitive": {
            "description": "General cognitive biases",
            "examples": ["confirmation bias", "anchoring bias", "availability bias"]
        },
        "confirmation": {
            "description": "Seeking confirming evidence",
            "examples": ["cherry-picking data", "ignoring counter-evidence"]
        },
        "anchoring": {
            "description": "Relying on first information",
            "examples": ["first impression bias", "initial value influence"]
        },
        "availability": {
            "description": "Overestimating memorable events",
            "examples": ["recency bias", "vividness bias"]
        },
        "gender": {
            "description": "Gender-related bias",
            "examples": ["stereotyping", "gendered language"]
        },
        "racial": {
            "description": "Race-related bias",
            "examples": ["racial stereotypes", "cultural bias"]
        },
        "political": {
            "description": "Political bias",
            "examples": ["partisan language", "ideological bias"]
        },
        "cultural": {
            "description": "Cultural bias",
            "examples": ["ethnocentrism", "cultural stereotypes"]
        },
        "linguistic": {
            "description": "Language-based bias",
            "examples": ["loaded language", "emotive terms"]
        }
    }
    
    return {
        "success": True,
        "bias_types": bias_types
    }

@router.get("/context-types")
async def get_context_types():
    """Get available context types for sentiment analysis"""
    
    context_types = {
        "general": {
            "description": "General sentiment analysis",
            "focus": ["Overall sentiment", "General tone", "Basic emotions"]
        },
        "business": {
            "description": "Business and professional context",
            "focus": ["Professional tone", "Business implications", "Stakeholder sentiment"]
        },
        "academic": {
            "description": "Academic and scholarly context",
            "focus": ["Scholarly tone", "Research implications", "Academic rigor"]
        },
        "legal": {
            "description": "Legal and regulatory context",
            "focus": ["Legal implications", "Compliance sentiment", "Regulatory tone"]
        },
        "medical": {
            "description": "Medical and healthcare context",
            "focus": ["Clinical tone", "Patient sentiment", "Medical implications"]
        },
        "customer_service": {
            "description": "Customer service context",
            "focus": ["Customer satisfaction", "Service quality", "Support sentiment"]
        },
        "marketing": {
            "description": "Marketing and advertising context",
            "focus": ["Brand sentiment", "Marketing effectiveness", "Consumer response"]
        }
    }
    
    return {
        "success": True,
        "context_types": context_types
    }
