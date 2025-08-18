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

class SentimentAnalysisAgent(BaseAgent):
    """Agent for analyzing document sentiment, tone, and emotional content"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(agent_type="sentiment", llm_model=llm_model)
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.1,
            max_tokens=4000,
            openai_api_key=settings.LLM_API_KEY
        )
        
        # Initialize tools
        self.tools = {
            "sentiment_analysis": self.sentiment_analysis_tool,
            "tone_analysis": self.tone_analysis_tool,
            "emotion_detection": self.emotion_detection_tool,
            "sentiment_tracking": self.sentiment_tracking_tool,
            "bias_detection": self.bias_detection_tool,
            "context_sentiment": self.context_sentiment_tool,
            "sentiment_comparison": self.sentiment_comparison_tool,
            "sentiment_validation": self.sentiment_validation_tool
        }
    
    def sentiment_analysis_tool(self, text: str, analysis_depth: str = "comprehensive") -> Dict[str, Any]:
        """Analyze overall sentiment of the text"""
        
        system_prompt = """You are an expert sentiment analysis specialist.
        Your task is to analyze the sentiment of text with high accuracy and provide detailed insights.
        
        Guidelines:
        - Analyze both explicit and implicit sentiment
        - Consider context and nuance
        - Identify sentiment polarity (positive, negative, neutral)
        - Assess sentiment intensity (strong, moderate, weak)
        - Consider mixed sentiments and contradictions
        - Account for sarcasm and irony when present
        
        Analysis depths:
        - basic: simple positive/negative/neutral classification
        - detailed: includes intensity and confidence scores
        - comprehensive: includes context, nuances, and detailed breakdown
        
        Return a JSON object with:
        - overall_sentiment: primary sentiment classification
        - sentiment_score: numerical sentiment score (-1 to 1)
        - sentiment_intensity: intensity level (strong, moderate, weak)
        - confidence_score: confidence in the analysis (0-1)
        - sentiment_breakdown: detailed breakdown by sections/paragraphs
        - key_sentiment_indicators: words/phrases that influenced sentiment
        - sentiment_context: contextual factors affecting sentiment
        - mixed_sentiments: any conflicting sentiments identified
        """
        
        human_prompt = f"""Text to analyze:
{text}

Perform {analysis_depth} sentiment analysis on this text.

Provide the analysis in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_sentiment_confidence(
                result.get("sentiment_score", 0),
                result.get("confidence_score", 0),
                len(text)
            )
            
            return {
                "overall_sentiment": result.get("overall_sentiment", "neutral"),
                "sentiment_score": result.get("sentiment_score", 0.0),
                "sentiment_intensity": result.get("sentiment_intensity", "moderate"),
                "confidence_score": confidence,
                "sentiment_breakdown": result.get("sentiment_breakdown", {}),
                "key_sentiment_indicators": result.get("key_sentiment_indicators", []),
                "sentiment_context": result.get("sentiment_context", ""),
                "mixed_sentiments": result.get("mixed_sentiments", []),
                "analysis_depth": analysis_depth
            }
            
        except Exception as e:
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0.0,
                "sentiment_intensity": "moderate",
                "confidence_score": 0.0,
                "sentiment_breakdown": {},
                "key_sentiment_indicators": [],
                "sentiment_context": f"Analysis error: {str(e)}",
                "mixed_sentiments": [],
                "analysis_depth": analysis_depth
            }
    
    def tone_analysis_tool(self, text: str, tone_categories: List[str] = None) -> Dict[str, Any]:
        """Analyze the tone and writing style of the text"""
        
        if not tone_categories:
            tone_categories = ["formal", "informal", "professional", "casual", "authoritative", "friendly", "neutral"]
        
        system_prompt = """You are an expert tone analysis specialist.
        Your task is to analyze the tone, writing style, and communication approach of text.
        
        Guidelines:
        - Identify primary and secondary tones
        - Assess formality level and register
        - Analyze communication style and approach
        - Consider audience and purpose
        - Evaluate tone consistency throughout the text
        - Identify tone shifts or variations
        
        Tone categories to consider:
        - formal/informal: level of formality
        - professional/casual: business vs. personal style
        - authoritative/friendly: power dynamics
        - neutral/emotional: emotional engagement
        - objective/subjective: perspective approach
        - confident/uncertain: certainty level
        - respectful/condescending: respect level
        
        Return a JSON object with:
        - primary_tone: the main tone identified
        - secondary_tones: additional tones present
        - formality_level: formality assessment
        - communication_style: overall communication approach
        - tone_consistency: consistency throughout the text
        - tone_shifts: any significant tone changes
        - audience_appropriateness: suitability for intended audience
        - confidence_score: confidence in the analysis (0-1)
        """
        
        categories_text = ", ".join(tone_categories)
        
        human_prompt = f"""Text to analyze:
{text}

Analyze the tone considering these categories: {categories_text}

Provide the tone analysis in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_tone_confidence(
                result.get("primary_tone", ""),
                result.get("secondary_tones", []),
                len(text)
            )
            
            return {
                "primary_tone": result.get("primary_tone", "neutral"),
                "secondary_tones": result.get("secondary_tones", []),
                "formality_level": result.get("formality_level", "moderate"),
                "communication_style": result.get("communication_style", ""),
                "tone_consistency": result.get("tone_consistency", "consistent"),
                "tone_shifts": result.get("tone_shifts", []),
                "audience_appropriateness": result.get("audience_appropriateness", ""),
                "confidence_score": confidence,
                "tone_categories": tone_categories
            }
            
        except Exception as e:
            return {
                "primary_tone": "neutral",
                "secondary_tones": [],
                "formality_level": "moderate",
                "communication_style": "",
                "tone_consistency": "consistent",
                "tone_shifts": [],
                "audience_appropriateness": "",
                "confidence_score": 0.0,
                "tone_categories": tone_categories,
                "error": str(e)
            }
    
    def emotion_detection_tool(self, text: str, emotion_categories: List[str] = None) -> Dict[str, Any]:
        """Detect specific emotions expressed in the text"""
        
        if not emotion_categories:
            emotion_categories = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation"]
        
        system_prompt = """You are an expert emotion detection specialist.
        Your task is to identify and analyze emotions expressed in text with high accuracy.
        
        Guidelines:
        - Identify primary and secondary emotions
        - Assess emotion intensity and duration
        - Consider emotional context and triggers
        - Analyze emotional complexity and mixed emotions
        - Identify emotional expressions and indicators
        - Consider cultural and contextual factors
        
        Emotion categories (Plutchik's wheel):
        - joy: happiness, pleasure, contentment
        - sadness: grief, sorrow, melancholy
        - anger: rage, frustration, irritation
        - fear: anxiety, worry, terror
        - surprise: astonishment, amazement, shock
        - disgust: aversion, repulsion, contempt
        - trust: confidence, faith, acceptance
        - anticipation: expectation, interest, vigilance
        
        Return a JSON object with:
        - primary_emotion: the most prominent emotion
        - secondary_emotions: other emotions present
        - emotion_intensities: intensity levels for each emotion
        - emotional_triggers: what caused the emotions
        - emotional_expressions: how emotions are expressed
        - emotional_complexity: complexity of emotional state
        - emotional_context: context affecting emotions
        - confidence_score: confidence in the analysis (0-1)
        """
        
        categories_text = ", ".join(emotion_categories)
        
        human_prompt = f"""Text to analyze:
{text}

Detect emotions considering these categories: {categories_text}

Provide the emotion detection in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_emotion_confidence(
                result.get("primary_emotion", ""),
                result.get("secondary_emotions", []),
                len(text)
            )
            
            return {
                "primary_emotion": result.get("primary_emotion", "neutral"),
                "secondary_emotions": result.get("secondary_emotions", []),
                "emotion_intensities": result.get("emotion_intensities", {}),
                "emotional_triggers": result.get("emotional_triggers", []),
                "emotional_expressions": result.get("emotional_expressions", []),
                "emotional_complexity": result.get("emotional_complexity", "simple"),
                "emotional_context": result.get("emotional_context", ""),
                "confidence_score": confidence,
                "emotion_categories": emotion_categories
            }
            
        except Exception as e:
            return {
                "primary_emotion": "neutral",
                "secondary_emotions": [],
                "emotion_intensities": {},
                "emotional_triggers": [],
                "emotional_expressions": [],
                "emotional_complexity": "simple",
                "emotional_context": "",
                "confidence_score": 0.0,
                "emotion_categories": emotion_categories,
                "error": str(e)
            }
    
    def sentiment_tracking_tool(self, text: str, tracking_granularity: str = "paragraph") -> Dict[str, Any]:
        """Track sentiment changes throughout the text"""
        
        system_prompt = """You are an expert in sentiment tracking and trend analysis.
        Your task is to track how sentiment changes throughout the text and identify patterns.
        
        Guidelines:
        - Track sentiment at specified granularity level
        - Identify sentiment trends and patterns
        - Detect sentiment shifts and transitions
        - Analyze sentiment flow and progression
        - Identify factors causing sentiment changes
        - Assess overall sentiment trajectory
        
        Granularity levels:
        - sentence: track sentiment by individual sentences
        - paragraph: track sentiment by paragraphs
        - section: track sentiment by document sections
        - overall: track major sentiment phases
        
        Return a JSON object with:
        - sentiment_timeline: sentiment scores over time
        - sentiment_trends: identified trends and patterns
        - sentiment_shifts: significant sentiment changes
        - sentiment_factors: factors influencing changes
        - sentiment_trajectory: overall sentiment direction
        - sentiment_stability: consistency of sentiment
        - confidence_score: confidence in the tracking (0-1)
        """
        
        human_prompt = f"""Text to analyze:
{text}

Track sentiment changes with {tracking_granularity} granularity.

Provide the sentiment tracking in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_tracking_confidence(
                result.get("sentiment_timeline", []),
                result.get("sentiment_shifts", []),
                len(text)
            )
            
            return {
                "sentiment_timeline": result.get("sentiment_timeline", []),
                "sentiment_trends": result.get("sentiment_trends", []),
                "sentiment_shifts": result.get("sentiment_shifts", []),
                "sentiment_factors": result.get("sentiment_factors", []),
                "sentiment_trajectory": result.get("sentiment_trajectory", "stable"),
                "sentiment_stability": result.get("sentiment_stability", "stable"),
                "confidence_score": confidence,
                "tracking_granularity": tracking_granularity
            }
            
        except Exception as e:
            return {
                "sentiment_timeline": [],
                "sentiment_trends": [],
                "sentiment_shifts": [],
                "sentiment_factors": [],
                "sentiment_trajectory": "stable",
                "sentiment_stability": "stable",
                "confidence_score": 0.0,
                "tracking_granularity": tracking_granularity,
                "error": str(e)
            }
    
    def bias_detection_tool(self, text: str, bias_types: List[str] = None) -> Dict[str, Any]:
        """Detect various types of bias in the text"""
        
        if not bias_types:
            bias_types = ["cognitive", "confirmation", "anchoring", "availability", "gender", "racial", "political"]
        
        system_prompt = """You are an expert bias detection specialist.
        Your task is to identify various types of bias present in text with high accuracy.
        
        Guidelines:
        - Identify different types of bias
        - Assess bias intensity and impact
        - Consider implicit and explicit bias
        - Analyze language patterns indicating bias
        - Evaluate objectivity and fairness
        - Consider cultural and contextual factors
        
        Bias types to consider:
        - cognitive: general cognitive biases
        - confirmation: seeking confirming evidence
        - anchoring: relying on first information
        - availability: overestimating memorable events
        - gender: gender-related bias
        - racial: race-related bias
        - political: political bias
        - cultural: cultural bias
        - linguistic: language-based bias
        
        Return a JSON object with:
        - detected_biases: list of identified biases
        - bias_intensities: intensity levels for each bias
        - bias_indicators: specific indicators of bias
        - objectivity_score: overall objectivity assessment
        - fairness_assessment: fairness evaluation
        - bias_impact: potential impact of biases
        - recommendations: suggestions for reducing bias
        - confidence_score: confidence in the analysis (0-1)
        """
        
        types_text = ", ".join(bias_types)
        
        human_prompt = f"""Text to analyze:
{text}

Detect bias considering these types: {types_text}

Provide the bias detection in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_bias_confidence(
                result.get("detected_biases", []),
                result.get("objectivity_score", 0.5),
                len(text)
            )
            
            return {
                "detected_biases": result.get("detected_biases", []),
                "bias_intensities": result.get("bias_intensities", {}),
                "bias_indicators": result.get("bias_indicators", []),
                "objectivity_score": result.get("objectivity_score", 0.5),
                "fairness_assessment": result.get("fairness_assessment", ""),
                "bias_impact": result.get("bias_impact", ""),
                "recommendations": result.get("recommendations", []),
                "confidence_score": confidence,
                "bias_types": bias_types
            }
            
        except Exception as e:
            return {
                "detected_biases": [],
                "bias_intensities": {},
                "bias_indicators": [],
                "objectivity_score": 0.5,
                "fairness_assessment": "",
                "bias_impact": "",
                "recommendations": [],
                "confidence_score": 0.0,
                "bias_types": bias_types,
                "error": str(e)
            }
    
    def context_sentiment_tool(self, text: str, context_type: str = "general") -> Dict[str, Any]:
        """Analyze sentiment in specific contexts"""
        
        system_prompt = """You are an expert in contextual sentiment analysis.
        Your task is to analyze sentiment within specific contexts and domains.
        
        Guidelines:
        - Consider domain-specific sentiment indicators
        - Analyze sentiment in context of purpose and audience
        - Assess appropriateness of sentiment for context
        - Consider cultural and situational factors
        - Evaluate sentiment effectiveness for context
        - Identify context-specific sentiment patterns
        
        Context types:
        - general: general sentiment analysis
        - business: business and professional context
        - academic: academic and scholarly context
        - legal: legal and regulatory context
        - medical: medical and healthcare context
        - customer_service: customer service context
        - marketing: marketing and advertising context
        
        Return a JSON object with:
        - contextual_sentiment: sentiment analysis for the specific context
        - context_appropriateness: appropriateness for the context
        - context_effectiveness: effectiveness in the context
        - context_specific_insights: insights specific to the context
        - context_recommendations: recommendations for the context
        - confidence_score: confidence in the analysis (0-1)
        """
        
        human_prompt = f"""Text to analyze:
{text}

Analyze sentiment in {context_type} context.

Provide the contextual sentiment analysis in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_context_confidence(
                result.get("contextual_sentiment", {}),
                context_type,
                len(text)
            )
            
            return {
                "contextual_sentiment": result.get("contextual_sentiment", {}),
                "context_appropriateness": result.get("context_appropriateness", ""),
                "context_effectiveness": result.get("context_effectiveness", ""),
                "context_specific_insights": result.get("context_specific_insights", []),
                "context_recommendations": result.get("context_recommendations", []),
                "confidence_score": confidence,
                "context_type": context_type
            }
            
        except Exception as e:
            return {
                "contextual_sentiment": {},
                "context_appropriateness": "",
                "context_effectiveness": "",
                "context_specific_insights": [],
                "context_recommendations": [],
                "confidence_score": 0.0,
                "context_type": context_type,
                "error": str(e)
            }
    
    def sentiment_comparison_tool(self, text_a: str, text_b: str, comparison_criteria: List[str] = None) -> Dict[str, Any]:
        """Compare sentiment between two texts"""
        
        if not comparison_criteria:
            comparison_criteria = ["overall_sentiment", "sentiment_intensity", "tone", "emotions"]
        
        system_prompt = """You are an expert in comparative sentiment analysis.
        Your task is to compare sentiment between two texts and identify differences and similarities.
        
        Guidelines:
        - Compare sentiment across multiple dimensions
        - Identify similarities and differences
        - Assess relative sentiment strength
        - Analyze sentiment patterns and trends
        - Consider contextual factors in comparison
        - Provide detailed comparative insights
        
        Comparison criteria:
        - overall_sentiment: general sentiment comparison
        - sentiment_intensity: intensity level comparison
        - tone: tone and style comparison
        - emotions: emotional content comparison
        - bias: bias level comparison
        - context_appropriateness: context suitability comparison
        
        Return a JSON object with:
        - comparison_results: detailed comparison for each criterion
        - similarities: shared sentiment characteristics
        - differences: distinct sentiment characteristics
        - relative_strengths: relative sentiment strength
        - comparative_insights: insights from the comparison
        - confidence_score: confidence in the comparison (0-1)
        """
        
        criteria_text = ", ".join(comparison_criteria)
        
        human_prompt = f"""Text A:
{text_a}

Text B:
{text_b}

Compare sentiment based on: {criteria_text}

Provide the sentiment comparison in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_comparison_confidence(
                result.get("comparison_results", {}),
                len(text_a) + len(text_b)
            )
            
            return {
                "comparison_results": result.get("comparison_results", {}),
                "similarities": result.get("similarities", []),
                "differences": result.get("differences", []),
                "relative_strengths": result.get("relative_strengths", {}),
                "comparative_insights": result.get("comparative_insights", []),
                "confidence_score": confidence,
                "comparison_criteria": comparison_criteria
            }
            
        except Exception as e:
            return {
                "comparison_results": {},
                "similarities": [],
                "differences": [],
                "relative_strengths": {},
                "comparative_insights": [],
                "confidence_score": 0.0,
                "comparison_criteria": comparison_criteria,
                "error": str(e)
            }
    
    def sentiment_validation_tool(self, text: str, sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate sentiment analysis results"""
        
        system_prompt = """You are an expert sentiment analysis validator.
        Your task is to validate the accuracy and reliability of sentiment analysis results.
        
        Guidelines:
        - Verify sentiment classification accuracy
        - Assess confidence level appropriateness
        - Check for consistency and coherence
        - Validate sentiment indicators
        - Evaluate analysis completeness
        - Identify potential errors or issues
        
        Return a JSON object with:
        - validation_results: detailed validation assessment
        - accuracy_assessment: accuracy evaluation
        - confidence_validation: confidence level validation
        - consistency_check: consistency assessment
        - completeness_evaluation: completeness check
        - error_identification: any errors or issues found
        - validation_score: overall validation score (0-1)
        """
        
        analysis_text = json.dumps(sentiment_analysis, indent=2)
        
        human_prompt = f"""Original text:
{text}

Sentiment analysis to validate:
{analysis_text}

Validate the sentiment analysis results.

Provide the validation in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Calculate overall validation score
            validation_score = result.get("validation_score", 0.0)
            
            return {
                "validation_results": result.get("validation_results", {}),
                "accuracy_assessment": result.get("accuracy_assessment", ""),
                "confidence_validation": result.get("confidence_validation", ""),
                "consistency_check": result.get("consistency_check", ""),
                "completeness_evaluation": result.get("completeness_evaluation", ""),
                "error_identification": result.get("error_identification", []),
                "validation_score": validation_score
            }
            
        except Exception as e:
            return {
                "validation_results": {},
                "accuracy_assessment": "",
                "confidence_validation": "",
                "consistency_check": "",
                "completeness_evaluation": "",
                "error_identification": [f"Validation error: {str(e)}"],
                "validation_score": 0.0
            }
    
    def _calculate_sentiment_confidence(self, sentiment_score: float, base_confidence: float, text_length: int) -> float:
        """Calculate confidence for sentiment analysis"""
        if text_length == 0:
            return 0.0
        
        # Base confidence from analysis
        base_score = base_confidence or 0.5
        
        # Length bonus (more text = more data)
        length_bonus = min(1.0, text_length / 500.0)
        
        # Sentiment score consistency bonus
        score_consistency = 1.0 - abs(sentiment_score) if sentiment_score is not None else 0.5
        
        return (base_score + length_bonus + score_consistency) / 3.0
    
    def _calculate_tone_confidence(self, primary_tone: str, secondary_tones: List[str], text_length: int) -> float:
        """Calculate confidence for tone analysis"""
        if not primary_tone or text_length == 0:
            return 0.0
        
        # Base confidence on having a primary tone
        tone_score = 0.8 if primary_tone else 0.0
        
        # Secondary tones bonus
        secondary_bonus = min(1.0, len(secondary_tones) / 3.0)
        
        # Length bonus
        length_bonus = min(1.0, text_length / 300.0)
        
        return (tone_score + secondary_bonus + length_bonus) / 3.0
    
    def _calculate_emotion_confidence(self, primary_emotion: str, secondary_emotions: List[str], text_length: int) -> float:
        """Calculate confidence for emotion detection"""
        if not primary_emotion or text_length == 0:
            return 0.0
        
        # Base confidence on having a primary emotion
        emotion_score = 0.8 if primary_emotion else 0.0
        
        # Secondary emotions bonus
        secondary_bonus = min(1.0, len(secondary_emotions) / 4.0)
        
        # Length bonus
        length_bonus = min(1.0, text_length / 400.0)
        
        return (emotion_score + secondary_bonus + length_bonus) / 3.0
    
    def _calculate_tracking_confidence(self, timeline: List[Dict], shifts: List[Dict], text_length: int) -> float:
        """Calculate confidence for sentiment tracking"""
        if not timeline or text_length == 0:
            return 0.0
        
        # Base confidence on having timeline data
        timeline_score = min(1.0, len(timeline) / 5.0)
        
        # Shifts detection bonus
        shifts_bonus = min(1.0, len(shifts) / 3.0)
        
        # Length bonus
        length_bonus = min(1.0, text_length / 600.0)
        
        return (timeline_score + shifts_bonus + length_bonus) / 3.0
    
    def _calculate_bias_confidence(self, biases: List[str], objectivity_score: float, text_length: int) -> float:
        """Calculate confidence for bias detection"""
        if text_length == 0:
            return 0.0
        
        # Base confidence on objectivity assessment
        objectivity_bonus = 1.0 - abs(objectivity_score - 0.5) * 2  # Higher confidence for extreme scores
        
        # Bias detection bonus
        bias_bonus = min(1.0, len(biases) / 5.0)
        
        # Length bonus
        length_bonus = min(1.0, text_length / 500.0)
        
        return (objectivity_bonus + bias_bonus + length_bonus) / 3.0
    
    def _calculate_context_confidence(self, context_sentiment: Dict, context_type: str, text_length: int) -> float:
        """Calculate confidence for contextual sentiment analysis"""
        if not context_sentiment or text_length == 0:
            return 0.0
        
        # Base confidence on having contextual analysis
        context_score = 0.7 if context_sentiment else 0.0
        
        # Context type specificity bonus
        specific_contexts = ["business", "legal", "medical", "academic"]
        specificity_bonus = 0.2 if context_type in specific_contexts else 0.1
        
        # Length bonus
        length_bonus = min(1.0, text_length / 400.0)
        
        return (context_score + specificity_bonus + length_bonus) / 3.0
    
    def _calculate_comparison_confidence(self, comparison_results: Dict, total_length: int) -> float:
        """Calculate confidence for sentiment comparison"""
        if not comparison_results or total_length == 0:
            return 0.0
        
        # Base confidence on having comparison results
        comparison_score = min(1.0, len(comparison_results) / 4.0)
        
        # Length bonus (more text to compare)
        length_bonus = min(1.0, total_length / 800.0)
        
        return (comparison_score + length_bonus) / 2.0
    
    async def execute(self, document_content: str, goal: str = "Analyze sentiment", 
                     **kwargs) -> AgentResult:
        """Execute the sentiment analysis agent"""
        
        try:
            # Determine analysis type from goal
            if "tone" in goal.lower():
                result = self.tone_analysis_tool(
                    document_content,
                    tone_categories=kwargs.get("tone_categories")
                )
            elif "emotion" in goal.lower():
                result = self.emotion_detection_tool(
                    document_content,
                    emotion_categories=kwargs.get("emotion_categories")
                )
            elif "bias" in goal.lower():
                result = self.bias_detection_tool(
                    document_content,
                    bias_types=kwargs.get("bias_types")
                )
            elif "tracking" in goal.lower():
                result = self.sentiment_tracking_tool(
                    document_content,
                    tracking_granularity=kwargs.get("tracking_granularity", "paragraph")
                )
            elif "context" in goal.lower():
                result = self.context_sentiment_tool(
                    document_content,
                    context_type=kwargs.get("context_type", "general")
                )
            else:  # default sentiment analysis
                result = self.sentiment_analysis_tool(
                    document_content,
                    analysis_depth=kwargs.get("analysis_depth", "comprehensive")
                )
            
            return AgentResult(
                output=result,
                confidence=result.get("confidence_score", 0.0),
                rationale=f"Performed sentiment analysis with {result.get('confidence_score', 0.0):.2f} confidence",
                execution_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return AgentResult(
                output={"error": str(e)},
                confidence=0.0,
                rationale=f"Error in sentiment analysis: {str(e)}",
                execution_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                timestamp=datetime.utcnow()
            )
