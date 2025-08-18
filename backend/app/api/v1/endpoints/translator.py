from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, Any, List, Optional
import logging

from ....services.agent_service import get_agent_service
from ....models.base import Document
from ....core.config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

@router.post("/translate")
async def translate_document(
    target_language: str,
    source_language: str = "auto",
    translation_style: str = "formal",
    preserve_terminology: bool = True,
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Translate document to target language"""
    try:
        agent_params = {
            "target_language": target_language,
            "source_language": source_language,
            "translation_style": translation_style,
            "preserve_terminology": preserve_terminology
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="translator",
            document=document,
            goal=f"Translate to {target_language}"
        )
        
        return {
            "status": "success",
            "target_language": target_language,
            "source_language": source_language,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in translation: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/translate-document")
async def translate_document_with_structure(
    target_language: str,
    document_type: str = "general",
    preserve_structure: bool = True,
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Translate entire document with structure preservation"""
    try:
        agent_params = {
            "target_language": target_language,
            "document_type": document_type,
            "preserve_structure": preserve_structure
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="translator",
            document=document,
            goal=f"Translate document to {target_language}"
        )
        
        return {
            "status": "success",
            "target_language": target_language,
            "document_type": document_type,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in document translation: {e}")
        raise HTTPException(status_code=500, detail=f"Document translation failed: {str(e)}")

@router.post("/detect-language")
async def detect_language(
    text: str,
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Detect the language of the input text"""
    try:
        # Create a mock document with the text
        detection_doc = Document(
            id=0,
            filename="language_detection",
            content=text,
            file_path="",
            file_size=0,
            content_type="text/plain"
        )
        
        result = await agent_service.execute_single_agent(
            agent_type="translator",
            document=detection_doc,
            goal="Detect language"
        )
        
        return {
            "status": "success",
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in language detection: {e}")
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")

@router.post("/technical-translation")
async def technical_translation(
    target_language: str,
    technical_domain: str = "general",
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Translate technical content with domain-specific terminology"""
    try:
        agent_params = {
            "target_language": target_language,
            "technical_domain": technical_domain
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="translator",
            document=document,
            goal=f"Technical translation to {target_language}"
        )
        
        return {
            "status": "success",
            "target_language": target_language,
            "technical_domain": technical_domain,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in technical translation: {e}")
        raise HTTPException(status_code=500, detail=f"Technical translation failed: {str(e)}")

@router.post("/cultural-adaptation")
async def cultural_adaptation(
    target_culture: str,
    adaptation_level: str = "moderate",
    text: str = None,
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Adapt content for target culture while maintaining meaning"""
    try:
        content = text if text else document.content
        
        # Create a mock document with the content
        adaptation_doc = Document(
            id=0,
            filename="cultural_adaptation",
            content=content,
            file_path="",
            file_size=0,
            content_type="text/plain"
        )
        
        agent_params = {
            "target_culture": target_culture,
            "adaptation_level": adaptation_level
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="translator",
            document=adaptation_doc,
            goal=f"Cultural adaptation for {target_culture}"
        )
        
        return {
            "status": "success",
            "target_culture": target_culture,
            "adaptation_level": adaptation_level,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in cultural adaptation: {e}")
        raise HTTPException(status_code=500, detail=f"Cultural adaptation failed: {str(e)}")

@router.post("/translation-validation")
async def validate_translation(
    original_text: str,
    translated_text: str,
    target_language: str,
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Validate translation quality and accuracy"""
    try:
        # Create a mock document with the validation data
        validation_doc = Document(
            id=0,
            filename="translation_validation",
            content=f"Original: {original_text}\n\nTranslated: {translated_text}",
            file_path="",
            file_size=0,
            content_type="text/plain"
        )
        
        agent_params = {
            "target_language": target_language
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="translator",
            document=validation_doc,
            goal="Validate translation"
        )
        
        return {
            "status": "success",
            "target_language": target_language,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in translation validation: {e}")
        raise HTTPException(status_code=500, detail=f"Translation validation failed: {str(e)}")

@router.post("/create-glossary")
async def create_glossary(
    target_language: str,
    domain: str = "general",
    document: Document = Depends(),
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Create a terminology glossary for translation"""
    try:
        agent_params = {
            "target_language": target_language,
            "domain": domain
        }
        
        result = await agent_service.execute_single_agent(
            agent_type="translator",
            document=document,
            goal=f"Create glossary for {domain} domain"
        )
        
        return {
            "status": "success",
            "target_language": target_language,
            "domain": domain,
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in glossary creation: {e}")
        raise HTTPException(status_code=500, detail=f"Glossary creation failed: {str(e)}")

@router.post("/preserve-formatting")
async def preserve_formatting(
    original_text: str,
    translated_text: str,
    agent_service = Depends(get_agent_service)
) -> Dict[str, Any]:
    """Preserve original formatting in translated text"""
    try:
        # Create a mock document with the formatting data
        formatting_doc = Document(
            id=0,
            filename="formatting_preservation",
            content=f"Original: {original_text}\n\nTranslated: {translated_text}",
            file_path="",
            file_size=0,
            content_type="text/plain"
        )
        
        result = await agent_service.execute_single_agent(
            agent_type="translator",
            document=formatting_doc,
            goal="Preserve formatting"
        )
        
        return {
            "status": "success",
            "result": result.output,
            "confidence": result.confidence,
            "rationale": result.rationale
        }
        
    except Exception as e:
        logger.error(f"Error in formatting preservation: {e}")
        raise HTTPException(status_code=500, detail=f"Formatting preservation failed: {str(e)}")

@router.get("/supported-languages")
async def get_supported_languages() -> Dict[str, Any]:
    """Get list of supported languages"""
    return {
        "supported_languages": {
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
    }

@router.get("/capabilities")
async def get_translator_capabilities() -> Dict[str, Any]:
    """Get available translator capabilities"""
    return {
        "translation_styles": [
            "formal",
            "informal",
            "technical",
            "literary"
        ],
        "document_types": [
            "general",
            "legal",
            "technical",
            "medical",
            "financial",
            "academic"
        ],
        "technical_domains": [
            "general",
            "software",
            "engineering",
            "medical",
            "legal",
            "financial",
            "scientific"
        ],
        "adaptation_levels": [
            "minimal",
            "moderate",
            "extensive"
        ],
        "features": [
            "translate_text",
            "translate_document",
            "detect_language",
            "preserve_formatting",
            "technical_translation",
            "cultural_adaptation",
            "translation_validation",
            "glossary_creation"
        ]
    }
