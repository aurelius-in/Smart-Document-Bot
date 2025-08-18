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

class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = "auto"
    translation_style: str = "formal"  # formal, informal, technical, literary
    preserve_terminology: bool = True

class DocumentTranslationRequest(BaseModel):
    document_content: str
    target_language: str
    document_type: str = "general"  # general, legal, technical, medical, financial, academic
    preserve_structure: bool = True

class TechnicalTranslationRequest(BaseModel):
    technical_text: str
    target_language: str
    technical_domain: str = "general"  # general, software, engineering, medical, legal, financial, scientific

class CulturalAdaptationRequest(BaseModel):
    text: str
    target_culture: str
    adaptation_level: str = "moderate"  # minimal, moderate, extensive

class TranslationValidationRequest(BaseModel):
    original_text: str
    translated_text: str
    target_language: str

class GlossaryRequest(BaseModel):
    text: str
    target_language: str
    domain: str = "general"

@router.post("/translate")
async def translate_text(
    request: TranslationRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Translate text to target language"""
    
    try:
        with monitor.agent_execution("translator", "translate_text"):
            result = await agent_service.execute_single_agent(
                agent_type="translator",
                document_content=request.text,
                goal="Translate text",
                target_language=request.target_language,
                source_language=request.source_language,
                translation_style=request.translation_style,
                preserve_terminology=request.preserve_terminology
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="translator",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "translation": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in text translation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/document")
async def translate_document(
    request: DocumentTranslationRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Translate entire document with structure preservation"""
    
    try:
        with monitor.agent_execution("translator", "translate_document"):
            result = await agent_service.execute_single_agent(
                agent_type="translator",
                document_content=request.document_content,
                goal="Translate document",
                target_language=request.target_language,
                document_type=request.document_type,
                preserve_structure=request.preserve_structure
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="translator",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "document_translation": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in document translation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document translation failed: {str(e)}")

@router.post("/detect-language")
async def detect_language(
    text: str,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Detect the language of the input text"""
    
    try:
        with monitor.agent_execution("translator", "detect_language"):
            result = await agent_service.execute_single_agent(
                agent_type="translator",
                document_content=text,
                goal="Detect language"
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="translator",
            execution_id=result.execution_id,
            input_data={"text": text},
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "language_detection": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in language detection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")

@router.post("/preserve-formatting")
async def preserve_formatting(
    original_text: str,
    translated_text: str,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Preserve original formatting in translated text"""
    
    try:
        with monitor.agent_execution("translator", "preserve_formatting"):
            result = await agent_service.execute_single_agent(
                agent_type="translator",
                document_content=f"Original: {original_text}\n\nTranslated: {translated_text}",
                goal="Preserve formatting"
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="translator",
            execution_id=result.execution_id,
            input_data={"original_text": original_text, "translated_text": translated_text},
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "formatted_translation": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in formatting preservation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Formatting preservation failed: {str(e)}")

@router.post("/technical")
async def technical_translation(
    request: TechnicalTranslationRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Translate technical content with domain-specific terminology"""
    
    try:
        with monitor.agent_execution("translator", "technical_translation"):
            result = await agent_service.execute_single_agent(
                agent_type="translator",
                document_content=request.technical_text,
                goal="Technical translation",
                target_language=request.target_language,
                technical_domain=request.technical_domain
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="translator",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "technical_translation": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in technical translation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Technical translation failed: {str(e)}")

@router.post("/cultural-adaptation")
async def cultural_adaptation(
    request: CulturalAdaptationRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Adapt content for target culture while maintaining meaning"""
    
    try:
        with monitor.agent_execution("translator", "cultural_adaptation"):
            result = await agent_service.execute_single_agent(
                agent_type="translator",
                document_content=request.text,
                goal="Cultural adaptation",
                target_culture=request.target_culture,
                adaptation_level=request.adaptation_level
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="translator",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "culturally_adapted_text": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in cultural adaptation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cultural adaptation failed: {str(e)}")

@router.post("/validate")
async def validate_translation(
    request: TranslationValidationRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Validate translation quality and accuracy"""
    
    try:
        with monitor.agent_execution("translator", "translation_validation"):
            result = await agent_service.execute_single_agent(
                agent_type="translator",
                document_content=f"Original: {request.original_text}\n\nTranslated: {request.translated_text}",
                goal="Validate translation",
                target_language=request.target_language
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="translator",
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
        logger.error(f"Error in translation validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation validation failed: {str(e)}")

@router.post("/glossary")
async def create_glossary(
    request: GlossaryRequest,
    background_tasks: BackgroundTasks,
    agent_service = Depends(get_agent_service),
    db = Depends(get_db)
):
    """Create a terminology glossary for translation"""
    
    try:
        with monitor.agent_execution("translator", "glossary_creation"):
            result = await agent_service.execute_single_agent(
                agent_type="translator",
                document_content=request.text,
                goal="Create glossary",
                target_language=request.target_language,
                domain=request.domain
            )
        
        # Log the trace
        background_tasks.add_task(
            agent_service.log_agent_trace,
            db=db,
            agent_type="translator",
            execution_id=result.execution_id,
            input_data=request.dict(),
            output_data=result.output,
            confidence=result.confidence,
            status="completed"
        )
        
        return {
            "success": True,
            "execution_id": result.execution_id,
            "glossary": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in glossary creation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Glossary creation failed: {str(e)}")

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    
    supported_languages = {
        "en": "English",
        "es": "Spanish", 
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "zh": "Chinese (Simplified)",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "hi": "Hindi",
        "nl": "Dutch",
        "sv": "Swedish",
        "no": "Norwegian",
        "da": "Danish",
        "fi": "Finnish",
        "pl": "Polish",
        "tr": "Turkish",
        "he": "Hebrew"
    }
    
    return {
        "success": True,
        "supported_languages": supported_languages
    }

@router.get("/translation-styles")
async def get_translation_styles():
    """Get available translation styles"""
    
    translation_styles = {
        "formal": {
            "description": "Professional and business-appropriate",
            "use_cases": ["Business documents", "Legal documents", "Academic papers"]
        },
        "informal": {
            "description": "Casual and conversational",
            "use_cases": ["Personal communication", "Blog posts", "Social media"]
        },
        "technical": {
            "description": "Precise and industry-specific",
            "use_cases": ["Technical documentation", "User manuals", "Scientific papers"]
        },
        "literary": {
            "description": "Artistic and creative",
            "use_cases": ["Creative writing", "Poetry", "Literature"]
        }
    }
    
    return {
        "success": True,
        "translation_styles": translation_styles
    }

@router.get("/document-types")
async def get_document_types():
    """Get supported document types for translation"""
    
    document_types = {
        "general": {
            "description": "General document translation",
            "features": ["Standard translation", "Basic formatting preservation"]
        },
        "legal": {
            "description": "Legal document with precise terminology",
            "features": ["Legal terminology", "Precise translation", "Compliance focus"]
        },
        "technical": {
            "description": "Technical document with specialized terms",
            "features": ["Technical terminology", "Specification preservation", "Accuracy focus"]
        },
        "medical": {
            "description": "Medical document with clinical terminology",
            "features": ["Medical terminology", "Clinical accuracy", "Safety focus"]
        },
        "financial": {
            "description": "Financial document with economic terms",
            "features": ["Financial terminology", "Regulatory compliance", "Precision focus"]
        },
        "academic": {
            "description": "Academic document with scholarly language",
            "features": ["Academic terminology", "Citation preservation", "Scholarly tone"]
        }
    }
    
    return {
        "success": True,
        "document_types": document_types
    }
