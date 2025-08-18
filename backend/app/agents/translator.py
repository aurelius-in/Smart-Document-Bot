from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime
import uuid

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from .base import BaseAgent, AgentResult
from ..core.config import get_settings

settings = get_settings()

class TranslatorAgent(BaseAgent):
    """Agent for translating documents between multiple languages"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(agent_type="translator", llm_model=llm_model)
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.1,
            max_tokens=4000,
            openai_api_key=settings.LLM_API_KEY
        )
        
        # Supported languages
        self.supported_languages = {
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
        
        # Initialize tools
        self.tools = {
            "translate_text": self.translate_text_tool,
            "translate_document": self.translate_document_tool,
            "detect_language": self.detect_language_tool,
            "preserve_formatting": self.preserve_formatting_tool,
            "technical_translation": self.technical_translation_tool,
            "cultural_adaptation": self.cultural_adaptation_tool,
            "translation_validation": self.translation_validation_tool,
            "glossary_creation": self.glossary_creation_tool
        }
    
    def translate_text_tool(self, text: str, target_language: str, source_language: str = "auto",
                          translation_style: str = "formal", preserve_terminology: bool = True) -> Dict[str, Any]:
        """Translate text to target language"""
        
        if target_language not in self.supported_languages:
            return {
                "translated_text": "",
                "confidence_score": 0.0,
                "error": f"Unsupported target language: {target_language}"
            }
        
        system_prompt = """You are an expert translator specializing in high-quality document translation.
        Your task is to translate text while preserving meaning, context, and technical accuracy.
        
        Guidelines:
        - Maintain the original meaning and intent
        - Preserve technical terminology and proper nouns
        - Adapt to the target language's cultural context
        - Use appropriate formality level
        - Ensure grammatical correctness
        - Preserve document structure and formatting
        
        Translation styles:
        - formal: professional, business-appropriate
        - informal: casual, conversational
        - technical: precise, industry-specific
        - literary: artistic, creative
        
        Return a JSON object with:
        - translated_text: the translated text
        - detected_source_language: detected source language
        - translation_notes: any important notes about the translation
        - preserved_terms: technical terms that were preserved
        - confidence_score: confidence in the translation quality (0-1)
        - cultural_adaptations: any cultural adaptations made
        """
        
        target_lang_name = self.supported_languages[target_language]
        source_lang_text = f" from {self.supported_languages.get(source_language, 'auto-detected')}" if source_language != "auto" else ""
        
        human_prompt = f"""Text to translate:
{text}

Translate to {target_lang_name}{source_lang_text} with style: {translation_style}
Preserve terminology: {preserve_terminology}

Provide the translation in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_translation_confidence(
                result.get("translated_text", ""),
                text,
                target_language
            )
            
            return {
                "translated_text": result.get("translated_text", ""),
                "detected_source_language": result.get("detected_source_language", source_language),
                "translation_notes": result.get("translation_notes", ""),
                "preserved_terms": result.get("preserved_terms", []),
                "confidence_score": confidence,
                "cultural_adaptations": result.get("cultural_adaptations", []),
                "target_language": target_language,
                "source_language": source_language,
                "translation_style": translation_style,
                "preserve_terminology": preserve_terminology
            }
            
        except Exception as e:
            return {
                "translated_text": "",
                "detected_source_language": source_language,
                "translation_notes": f"Translation error: {str(e)}",
                "preserved_terms": [],
                "confidence_score": 0.0,
                "cultural_adaptations": [],
                "target_language": target_language,
                "source_language": source_language,
                "translation_style": translation_style,
                "preserve_terminology": preserve_terminology
            }
    
    def translate_document_tool(self, document_content: str, target_language: str, 
                              document_type: str = "general", preserve_structure: bool = True) -> Dict[str, Any]:
        """Translate entire document with structure preservation"""
        
        system_prompt = """You are an expert document translator specializing in preserving document structure and formatting.
        Your task is to translate a complete document while maintaining its organization, sections, and formatting.
        
        Guidelines:
        - Preserve document structure (headings, sections, paragraphs)
        - Maintain formatting markers and special characters
        - Translate content while keeping layout intact
        - Preserve technical terminology and proper nouns
        - Maintain document tone and style
        - Ensure consistency throughout the document
        
        Document types:
        - general: standard document translation
        - legal: legal document with precise terminology
        - technical: technical document with specialized terms
        - medical: medical document with clinical terminology
        - financial: financial document with economic terms
        - academic: academic document with scholarly language
        
        Return a JSON object with:
        - translated_document: the complete translated document
        - structure_preserved: whether document structure was maintained
        - section_translations: translation details for each section
        - terminology_glossary: specialized terms and their translations
        - formatting_notes: notes about preserved formatting
        - confidence_score: confidence in the translation quality (0-1)
        """
        
        target_lang_name = self.supported_languages[target_language]
        
        human_prompt = f"""Document content:
{document_content}

Translate this {document_type} document to {target_lang_name}.
Preserve structure: {preserve_structure}

Provide the translation in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_document_translation_confidence(
                result.get("translated_document", ""),
                document_content,
                result.get("structure_preserved", False)
            )
            
            return {
                "translated_document": result.get("translated_document", ""),
                "structure_preserved": result.get("structure_preserved", False),
                "section_translations": result.get("section_translations", {}),
                "terminology_glossary": result.get("terminology_glossary", {}),
                "formatting_notes": result.get("formatting_notes", ""),
                "confidence_score": confidence,
                "target_language": target_language,
                "document_type": document_type,
                "preserve_structure": preserve_structure
            }
            
        except Exception as e:
            return {
                "translated_document": "",
                "structure_preserved": False,
                "section_translations": {},
                "terminology_glossary": {},
                "formatting_notes": f"Translation error: {str(e)}",
                "confidence_score": 0.0,
                "target_language": target_language,
                "document_type": document_type,
                "preserve_structure": preserve_structure
            }
    
    def detect_language_tool(self, text: str) -> Dict[str, Any]:
        """Detect the language of the input text"""
        
        system_prompt = """You are an expert language detection specialist.
        Your task is to identify the language of the provided text with high accuracy.
        
        Guidelines:
        - Analyze linguistic patterns, vocabulary, and grammar
        - Consider writing system (alphabet, script)
        - Identify regional variations and dialects
        - Provide confidence level for the detection
        - Handle mixed-language content
        
        Return a JSON object with:
        - detected_language: the detected language code
        - language_name: full name of the detected language
        - confidence_score: confidence in the detection (0-1)
        - alternative_languages: other possible languages
        - language_features: linguistic features identified
        - regional_variants: any regional variations detected
        """
        
        human_prompt = f"""Text to analyze:
{text}

Detect the language of this text.

Provide the detection results in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_language_detection_confidence(
                result.get("detected_language", ""),
                text
            )
            
            return {
                "detected_language": result.get("detected_language", ""),
                "language_name": result.get("language_name", ""),
                "confidence_score": confidence,
                "alternative_languages": result.get("alternative_languages", []),
                "language_features": result.get("language_features", []),
                "regional_variants": result.get("regional_variants", []),
                "text_sample": text[:100] + "..." if len(text) > 100 else text
            }
            
        except Exception as e:
            return {
                "detected_language": "",
                "language_name": "",
                "confidence_score": 0.0,
                "alternative_languages": [],
                "language_features": [],
                "regional_variants": [],
                "text_sample": text[:100] + "..." if len(text) > 100 else text,
                "error": str(e)
            }
    
    def preserve_formatting_tool(self, original_text: str, translated_text: str) -> Dict[str, Any]:
        """Preserve original formatting in translated text"""
        
        system_prompt = """You are an expert in document formatting preservation.
        Your task is to ensure that the translated text maintains the same formatting as the original.
        
        Guidelines:
        - Preserve paragraph breaks and line spacing
        - Maintain heading levels and structure
        - Keep bullet points and numbered lists
        - Preserve bold, italic, and other text formatting
        - Maintain table structures and alignments
        - Preserve special characters and symbols
        - Keep indentation and spacing consistent
        
        Return a JSON object with:
        - formatted_translation: the translation with preserved formatting
        - formatting_preserved: list of preserved formatting elements
        - formatting_issues: any formatting problems encountered
        - formatting_notes: notes about formatting decisions
        - confidence_score: confidence in formatting preservation (0-1)
        """
        
        human_prompt = f"""Original text with formatting:
{original_text}

Translated text:
{translated_text}

Preserve the original formatting in the translated text.

Provide the formatted translation in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_formatting_confidence(
                result.get("formatted_translation", ""),
                original_text
            )
            
            return {
                "formatted_translation": result.get("formatted_translation", ""),
                "formatting_preserved": result.get("formatting_preserved", []),
                "formatting_issues": result.get("formatting_issues", []),
                "formatting_notes": result.get("formatting_notes", ""),
                "confidence_score": confidence,
                "original_length": len(original_text),
                "translated_length": len(translated_text)
            }
            
        except Exception as e:
            return {
                "formatted_translation": translated_text,
                "formatting_preserved": [],
                "formatting_issues": [f"Error in formatting preservation: {str(e)}"],
                "formatting_notes": "Fallback to original translation",
                "confidence_score": 0.0,
                "original_length": len(original_text),
                "translated_length": len(translated_text)
            }
    
    def technical_translation_tool(self, technical_text: str, target_language: str, 
                                 technical_domain: str = "general") -> Dict[str, Any]:
        """Translate technical content with domain-specific terminology"""
        
        system_prompt = """You are an expert technical translator specializing in domain-specific terminology.
        Your task is to translate technical content while maintaining accuracy and using appropriate technical terms.
        
        Guidelines:
        - Use established technical terminology in the target language
        - Maintain technical accuracy and precision
        - Preserve technical concepts and relationships
        - Use appropriate technical register
        - Ensure consistency with industry standards
        - Provide explanations for complex terms when necessary
        
        Technical domains:
        - general: general technical content
        - software: software development and IT
        - engineering: mechanical, electrical, civil engineering
        - medical: medical and healthcare terminology
        - legal: legal and regulatory terminology
        - financial: financial and economic terms
        - scientific: scientific research and methodology
        
        Return a JSON object with:
        - technical_translation: the translated technical content
        - technical_terms: specialized terms and their translations
        - domain_accuracy: assessment of domain-specific accuracy
        - technical_notes: notes about technical translation decisions
        - confidence_score: confidence in the technical translation (0-1)
        """
        
        target_lang_name = self.supported_languages[target_language]
        
        human_prompt = f"""Technical content:
{technical_text}

Translate this {technical_domain} content to {target_lang_name}.

Provide the technical translation in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_technical_translation_confidence(
                result.get("technical_translation", ""),
                technical_text,
                technical_domain
            )
            
            return {
                "technical_translation": result.get("technical_translation", ""),
                "technical_terms": result.get("technical_terms", {}),
                "domain_accuracy": result.get("domain_accuracy", ""),
                "technical_notes": result.get("technical_notes", ""),
                "confidence_score": confidence,
                "target_language": target_language,
                "technical_domain": technical_domain
            }
            
        except Exception as e:
            return {
                "technical_translation": "",
                "technical_terms": {},
                "domain_accuracy": "",
                "technical_notes": f"Technical translation error: {str(e)}",
                "confidence_score": 0.0,
                "target_language": target_language,
                "technical_domain": technical_domain
            }
    
    def cultural_adaptation_tool(self, text: str, target_culture: str, 
                               adaptation_level: str = "moderate") -> Dict[str, Any]:
        """Adapt content for target culture while maintaining meaning"""
        
        system_prompt = """You are an expert in cultural adaptation and localization.
        Your task is to adapt content for a specific target culture while preserving the original meaning.
        
        Guidelines:
        - Adapt cultural references and idioms
        - Adjust examples and analogies for cultural relevance
        - Modify date/time formats and units of measurement
        - Adapt humor and tone for cultural appropriateness
        - Consider cultural sensitivities and taboos
        - Maintain the original message and intent
        
        Adaptation levels:
        - minimal: preserve most original cultural elements
        - moderate: adapt cultural references while keeping structure
        - extensive: significant cultural adaptation for local relevance
        
        Return a JSON object with:
        - culturally_adapted_text: the adapted content
        - cultural_changes: list of cultural adaptations made
        - cultural_notes: explanations of cultural decisions
        - adaptation_level: the level of adaptation applied
        - confidence_score: confidence in the cultural adaptation (0-1)
        """
        
        human_prompt = f"""Original text:
{text}

Adapt this content for {target_culture} culture with {adaptation_level} adaptation level.

Provide the cultural adaptation in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_cultural_adaptation_confidence(
                result.get("culturally_adapted_text", ""),
                text,
                adaptation_level
            )
            
            return {
                "culturally_adapted_text": result.get("culturally_adapted_text", ""),
                "cultural_changes": result.get("cultural_changes", []),
                "cultural_notes": result.get("cultural_notes", ""),
                "adaptation_level": adaptation_level,
                "confidence_score": confidence,
                "target_culture": target_culture
            }
            
        except Exception as e:
            return {
                "culturally_adapted_text": text,
                "cultural_changes": [],
                "cultural_notes": f"Cultural adaptation error: {str(e)}",
                "adaptation_level": adaptation_level,
                "confidence_score": 0.0,
                "target_culture": target_culture
            }
    
    def translation_validation_tool(self, original_text: str, translated_text: str, 
                                  target_language: str) -> Dict[str, Any]:
        """Validate translation quality and accuracy"""
        
        system_prompt = """You are an expert translation validator.
        Your task is to assess the quality and accuracy of a translation.
        
        Guidelines:
        - Check for meaning preservation
        - Assess grammatical correctness
        - Verify terminology accuracy
        - Evaluate fluency and naturalness
        - Check for omissions or additions
        - Assess cultural appropriateness
        
        Return a JSON object with:
        - validation_results: detailed validation assessment
        - accuracy_score: accuracy score (0-1)
        - fluency_score: fluency score (0-1)
        - completeness_score: completeness score (0-1)
        - errors_found: list of translation errors
        - suggestions: improvement suggestions
        - confidence_score: confidence in the validation (0-1)
        """
        
        target_lang_name = self.supported_languages[target_language]
        
        human_prompt = f"""Original text:
{original_text}

Translated text ({target_lang_name}):
{translated_text}

Validate the translation quality and accuracy.

Provide the validation results in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Calculate overall confidence
            scores = [
                result.get("accuracy_score", 0),
                result.get("fluency_score", 0),
                result.get("completeness_score", 0)
            ]
            overall_confidence = sum(scores) / len(scores) if scores else 0.0
            
            return {
                "validation_results": result.get("validation_results", {}),
                "accuracy_score": result.get("accuracy_score", 0.0),
                "fluency_score": result.get("fluency_score", 0.0),
                "completeness_score": result.get("completeness_score", 0.0),
                "errors_found": result.get("errors_found", []),
                "suggestions": result.get("suggestions", []),
                "confidence_score": overall_confidence,
                "target_language": target_language
            }
            
        except Exception as e:
            return {
                "validation_results": {},
                "accuracy_score": 0.0,
                "fluency_score": 0.0,
                "completeness_score": 0.0,
                "errors_found": [f"Validation error: {str(e)}"],
                "suggestions": [],
                "confidence_score": 0.0,
                "target_language": target_language
            }
    
    def glossary_creation_tool(self, text: str, target_language: str, 
                             domain: str = "general") -> Dict[str, Any]:
        """Create a terminology glossary for translation"""
        
        system_prompt = """You are an expert in terminology management and glossary creation.
        Your task is to identify and create a glossary of important terms for translation.
        
        Guidelines:
        - Identify domain-specific terminology
        - Include technical terms and proper nouns
        - Provide context and definitions
        - Suggest appropriate translations
        - Organize terms by importance and frequency
        - Include usage examples when helpful
        
        Return a JSON object with:
        - glossary_terms: list of identified terms with definitions
        - suggested_translations: suggested translations for each term
        - term_frequency: frequency of each term in the text
        - domain_specific_terms: domain-specific terminology
        - confidence_score: confidence in the glossary quality (0-1)
        """
        
        target_lang_name = self.supported_languages[target_language]
        
        human_prompt = f"""Text to analyze:
{text}

Create a terminology glossary for {domain} domain translation to {target_lang_name}.

Provide the glossary in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_glossary_confidence(
                result.get("glossary_terms", []),
                text
            )
            
            return {
                "glossary_terms": result.get("glossary_terms", []),
                "suggested_translations": result.get("suggested_translations", {}),
                "term_frequency": result.get("term_frequency", {}),
                "domain_specific_terms": result.get("domain_specific_terms", []),
                "confidence_score": confidence,
                "target_language": target_language,
                "domain": domain
            }
            
        except Exception as e:
            return {
                "glossary_terms": [],
                "suggested_translations": {},
                "term_frequency": {},
                "domain_specific_terms": [],
                "confidence_score": 0.0,
                "target_language": target_language,
                "domain": domain,
                "error": str(e)
            }
    
    def _calculate_translation_confidence(self, translated_text: str, original_text: str, target_language: str) -> float:
        """Calculate confidence for text translation"""
        if not translated_text or not original_text:
            return 0.0
        
        # Base confidence on length preservation
        length_ratio = len(translated_text) / len(original_text)
        optimal_ratio = 1.2  # Translations are often slightly longer
        
        ratio_confidence = 1.0 - abs(length_ratio - optimal_ratio) / optimal_ratio
        ratio_confidence = max(0.0, min(1.0, ratio_confidence))
        
        # Bonus for having content
        content_bonus = min(1.0, len(translated_text) / 100.0)
        
        return (ratio_confidence + content_bonus) / 2.0
    
    def _calculate_document_translation_confidence(self, translated_doc: str, original_doc: str, structure_preserved: bool) -> float:
        """Calculate confidence for document translation"""
        if not translated_doc or not original_doc:
            return 0.0
        
        # Base confidence on structure preservation
        structure_score = 1.0 if structure_preserved else 0.5
        
        # Length ratio confidence
        length_ratio = len(translated_doc) / len(original_doc)
        optimal_ratio = 1.1
        ratio_confidence = 1.0 - abs(length_ratio - optimal_ratio) / optimal_ratio
        ratio_confidence = max(0.0, min(1.0, ratio_confidence))
        
        return (structure_score + ratio_confidence) / 2.0
    
    def _calculate_language_detection_confidence(self, detected_lang: str, text: str) -> float:
        """Calculate confidence for language detection"""
        if not detected_lang or not text:
            return 0.0
        
        # Base confidence on having a detected language
        lang_score = 1.0 if detected_lang in self.supported_languages else 0.5
        
        # Bonus for longer text (more data for detection)
        length_bonus = min(1.0, len(text) / 500.0)
        
        return (lang_score + length_bonus) / 2.0
    
    def _calculate_formatting_confidence(self, formatted_text: str, original_text: str) -> float:
        """Calculate confidence for formatting preservation"""
        if not formatted_text or not original_text:
            return 0.0
        
        # Check for common formatting elements
        formatting_elements = ["\n\n", "\t", "  ", "*", "-", "1.", "2."]
        preserved_elements = sum(1 for elem in formatting_elements if elem in original_text and elem in formatted_text)
        
        element_score = preserved_elements / len(formatting_elements) if formatting_elements else 0.0
        
        # Length preservation bonus
        length_ratio = len(formatted_text) / len(original_text)
        length_score = 1.0 - abs(length_ratio - 1.0)
        
        return (element_score + length_score) / 2.0
    
    def _calculate_technical_translation_confidence(self, tech_translation: str, original_text: str, domain: str) -> float:
        """Calculate confidence for technical translation"""
        if not tech_translation or not original_text:
            return 0.0
        
        # Base confidence on having technical content
        tech_terms = ["system", "process", "method", "analysis", "data", "function", "parameter"]
        tech_term_count = sum(1 for term in tech_terms if term.lower() in original_text.lower())
        tech_score = min(1.0, tech_term_count / 3.0)
        
        # Translation length confidence
        length_ratio = len(tech_translation) / len(original_text)
        length_score = 1.0 - abs(length_ratio - 1.1)
        
        return (tech_score + length_score) / 2.0
    
    def _calculate_cultural_adaptation_confidence(self, adapted_text: str, original_text: str, adaptation_level: str) -> float:
        """Calculate confidence for cultural adaptation"""
        if not adapted_text or not original_text:
            return 0.0
        
        # Base confidence on adaptation level
        level_scores = {"minimal": 0.8, "moderate": 0.9, "extensive": 0.7}
        level_score = level_scores.get(adaptation_level, 0.8)
        
        # Content preservation confidence
        content_ratio = len(adapted_text) / len(original_text)
        content_score = 1.0 - abs(content_ratio - 1.0)
        
        return (level_score + content_score) / 2.0
    
    def _calculate_glossary_confidence(self, glossary_terms: List[Dict], text: str) -> float:
        """Calculate confidence for glossary creation"""
        if not glossary_terms or not text:
            return 0.0
        
        # Base confidence on number of terms
        term_count = len(glossary_terms)
        term_score = min(1.0, term_count / 10.0)
        
        # Text length bonus
        length_bonus = min(1.0, len(text) / 1000.0)
        
        return (term_score + length_bonus) / 2.0
    
    async def execute(self, document_content: str, goal: str = "Translate document", 
                     **kwargs) -> AgentResult:
        """Execute the translator agent"""
        
        try:
            target_language = kwargs.get("target_language", "en")
            source_language = kwargs.get("source_language", "auto")
            
            # Determine translation type from goal
            if "technical" in goal.lower():
                result = self.technical_translation_tool(
                    document_content,
                    target_language,
                    technical_domain=kwargs.get("technical_domain", "general")
                )
            elif "document" in goal.lower():
                result = self.translate_document_tool(
                    document_content,
                    target_language,
                    document_type=kwargs.get("document_type", "general")
                )
            else:
                result = self.translate_text_tool(
                    document_content,
                    target_language,
                    source_language=source_language,
                    translation_style=kwargs.get("translation_style", "formal")
                )
            
            return AgentResult(
                output=result,
                confidence=result.get("confidence_score", 0.0),
                rationale=f"Translated to {self.supported_languages.get(target_language, target_language)} with {result.get('confidence_score', 0.0):.2f} confidence",
                execution_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return AgentResult(
                output={"error": str(e)},
                confidence=0.0,
                rationale=f"Error in translation: {str(e)}",
                execution_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                timestamp=datetime.utcnow()
            )
