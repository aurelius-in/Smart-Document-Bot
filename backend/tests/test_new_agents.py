import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json

from app.agents.summarizer import SummarizerAgent
from app.agents.translator import TranslatorAgent
from app.agents.sentiment import SentimentAnalysisAgent
from app.services.agent_service import AgentService
from app.core.config import get_settings

settings = get_settings()

class TestSummarizerAgent:
    """Test cases for SummarizerAgent"""
    
    @pytest.fixture
    def summarizer_agent(self):
        """Create a SummarizerAgent instance for testing"""
        return SummarizerAgent()
    
    @pytest.fixture
    def sample_document(self):
        """Sample document content for testing"""
        return """
        Artificial Intelligence (AI) is transforming the way we work and live. 
        Machine learning algorithms are being used in various industries including healthcare, 
        finance, and transportation. The development of large language models has opened 
        new possibilities for natural language processing and understanding.
        
        However, there are also concerns about the ethical implications of AI systems. 
        Issues such as bias in algorithms, privacy concerns, and job displacement need 
        to be carefully considered. Organizations must implement responsible AI practices 
        to ensure these technologies benefit society as a whole.
        
        The future of AI looks promising with continued advancements in deep learning, 
        computer vision, and robotics. Companies are investing heavily in AI research 
        and development to gain competitive advantages in their respective markets.
        """
    
    @pytest.mark.asyncio
    async def test_extractive_summary_tool(self, summarizer_agent, sample_document):
        """Test extractive summary generation"""
        with patch.object(summarizer_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "summary": "AI is transforming industries. Machine learning is used in healthcare and finance. Ethical concerns exist about bias and privacy.",
                "selected_sentences": [0, 1, 4],
                "key_topics": ["AI transformation", "Machine learning", "Ethical concerns"],
                "confidence_score": 0.85,
                "rationale": "Selected key sentences that capture main ideas"
            })
            mock_invoke.return_value = mock_response
            
            result = summarizer_agent.extractive_summary_tool(sample_document, "medium")
            
            assert result["summary"] is not None
            assert result["confidence_score"] > 0
            assert len(result["selected_sentences"]) > 0
            assert result["extraction_method"] == "extractive"
    
    @pytest.mark.asyncio
    async def test_abstractive_summary_tool(self, summarizer_agent, sample_document):
        """Test abstractive summary generation"""
        with patch.object(summarizer_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "summary": "AI technology is revolutionizing multiple sectors through machine learning applications, while raising important ethical considerations about bias and privacy that require responsible implementation.",
                "main_ideas": ["AI transformation", "Ethical concerns", "Responsible implementation"],
                "tone": "informative",
                "confidence_score": 0.88,
                "rationale": "Created coherent summary capturing key themes"
            })
            mock_invoke.return_value = mock_response
            
            result = summarizer_agent.abstractive_summary_tool(sample_document, "informative", "general")
            
            assert result["summary"] is not None
            assert result["confidence_score"] > 0
            assert len(result["main_ideas"]) > 0
            assert result["extraction_method"] == "abstractive"
    
    @pytest.mark.asyncio
    async def test_executive_summary_tool(self, summarizer_agent, sample_document):
        """Test executive summary generation"""
        with patch.object(summarizer_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "executive_summary": "AI presents significant opportunities for business transformation but requires careful ethical consideration.",
                "key_findings": ["AI is transforming industries", "Ethical concerns exist"],
                "recommendations": ["Implement responsible AI practices", "Address bias and privacy concerns"],
                "business_impact": "High potential for competitive advantage",
                "risk_assessment": "Medium risk due to ethical considerations",
                "confidence_score": 0.82
            })
            mock_invoke.return_value = mock_response
            
            result = summarizer_agent.executive_summary_tool(sample_document, "general")
            
            assert result["executive_summary"] is not None
            assert len(result["key_findings"]) > 0
            assert len(result["recommendations"]) > 0
            assert result["summary_type"] == "executive"
    
    @pytest.mark.asyncio
    async def test_technical_summary_tool(self, summarizer_agent, sample_document):
        """Test technical summary generation"""
        with patch.object(summarizer_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "technical_summary": "The document discusses AI implementation using machine learning algorithms across healthcare, finance, and transportation sectors.",
                "technical_specifications": ["Machine learning algorithms", "Large language models"],
                "methodologies": ["Deep learning", "Computer vision"],
                "technical_findings": ["AI transformation in industries", "Ethical considerations"],
                "technical_challenges": ["Bias in algorithms", "Privacy concerns"],
                "confidence_score": 0.85
            })
            mock_invoke.return_value = mock_response
            
            result = summarizer_agent.technical_summary_tool(sample_document, "general")
            
            assert result["technical_summary"] is not None
            assert len(result["technical_specifications"]) > 0
            assert result["summary_type"] == "technical"
    
    @pytest.mark.asyncio
    async def test_execute_method(self, summarizer_agent, sample_document):
        """Test the main execute method"""
        with patch.object(summarizer_agent, 'abstractive_summary_tool') as mock_tool:
            mock_tool.return_value = {
                "summary": "Test summary",
                "confidence_score": 0.85
            }
            
            result = await summarizer_agent.execute(sample_document, "Generate summary")
            
            assert result.output is not None
            assert result.confidence > 0
            assert result.agent_type == "summarizer"

class TestTranslatorAgent:
    """Test cases for TranslatorAgent"""
    
    @pytest.fixture
    def translator_agent(self):
        """Create a TranslatorAgent instance for testing"""
        return TranslatorAgent()
    
    @pytest.fixture
    def sample_text(self):
        """Sample text for translation testing"""
        return "Artificial Intelligence is transforming the world through machine learning and deep learning technologies."
    
    @pytest.mark.asyncio
    async def test_translate_text_tool(self, translator_agent, sample_text):
        """Test text translation"""
        with patch.object(translator_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "translated_text": "La Inteligencia Artificial está transformando el mundo a través de tecnologías de aprendizaje automático y aprendizaje profundo.",
                "detected_source_language": "en",
                "translation_notes": "Technical terms preserved",
                "preserved_terms": ["Artificial Intelligence", "machine learning"],
                "confidence_score": 0.92,
                "cultural_adaptations": []
            })
            mock_invoke.return_value = mock_response
            
            result = translator_agent.translate_text_tool(sample_text, "es", "en", "formal", True)
            
            assert result["translated_text"] is not None
            assert result["confidence_score"] > 0
            assert result["target_language"] == "es"
            assert result["translation_style"] == "formal"
    
    @pytest.mark.asyncio
    async def test_detect_language_tool(self, translator_agent, sample_text):
        """Test language detection"""
        with patch.object(translator_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "detected_language": "en",
                "language_name": "English",
                "confidence_score": 0.95,
                "alternative_languages": [],
                "language_features": ["Latin alphabet", "English vocabulary"],
                "regional_variants": ["American English"]
            })
            mock_invoke.return_value = mock_response
            
            result = translator_agent.detect_language_tool(sample_text)
            
            assert result["detected_language"] == "en"
            assert result["confidence_score"] > 0
            assert result["language_name"] == "English"
    
    @pytest.mark.asyncio
    async def test_technical_translation_tool(self, translator_agent, sample_text):
        """Test technical translation"""
        with patch.object(translator_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "technical_translation": "L'Intelligence Artificielle transforme le monde grâce aux technologies d'apprentissage automatique et d'apprentissage profond.",
                "technical_terms": {
                    "Artificial Intelligence": "Intelligence Artificielle",
                    "machine learning": "apprentissage automatique"
                },
                "domain_accuracy": "High accuracy for technical terms",
                "technical_notes": "Preserved technical terminology",
                "confidence_score": 0.89
            })
            mock_invoke.return_value = mock_response
            
            result = translator_agent.technical_translation_tool(sample_text, "fr", "software")
            
            assert result["technical_translation"] is not None
            assert len(result["technical_terms"]) > 0
            assert result["technical_domain"] == "software"
    
    @pytest.mark.asyncio
    async def test_cultural_adaptation_tool(self, translator_agent, sample_text):
        """Test cultural adaptation"""
        with patch.object(translator_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "culturally_adapted_text": "AI technology is revolutionizing our world through advanced learning systems.",
                "cultural_changes": ["Simplified technical terms", "More accessible language"],
                "cultural_notes": "Adapted for general audience",
                "adaptation_level": "moderate",
                "confidence_score": 0.87
            })
            mock_invoke.return_value = mock_response
            
            result = translator_agent.cultural_adaptation_tool(sample_text, "American", "moderate")
            
            assert result["culturally_adapted_text"] is not None
            assert len(result["cultural_changes"]) > 0
            assert result["adaptation_level"] == "moderate"
    
    @pytest.mark.asyncio
    async def test_execute_method(self, translator_agent, sample_text):
        """Test the main execute method"""
        with patch.object(translator_agent, 'translate_text_tool') as mock_tool:
            mock_tool.return_value = {
                "translated_text": "Test translation",
                "confidence_score": 0.85
            }
            
            result = await translator_agent.execute(sample_text, "Translate document", target_language="es")
            
            assert result.output is not None
            assert result.confidence > 0
            assert result.agent_type == "translator"

class TestSentimentAnalysisAgent:
    """Test cases for SentimentAnalysisAgent"""
    
    @pytest.fixture
    def sentiment_agent(self):
        """Create a SentimentAnalysisAgent instance for testing"""
        return SentimentAnalysisAgent()
    
    @pytest.fixture
    def sample_text(self):
        """Sample text for sentiment analysis testing"""
        return "I am very excited about the new AI technology. It's amazing how it can help us solve complex problems. However, I'm also concerned about the potential risks and ethical implications."
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_tool(self, sentiment_agent, sample_text):
        """Test sentiment analysis"""
        with patch.object(sentiment_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "overall_sentiment": "mixed",
                "sentiment_score": 0.2,
                "sentiment_intensity": "moderate",
                "confidence_score": 0.88,
                "sentiment_breakdown": {
                    "positive": ["excited", "amazing"],
                    "negative": ["concerned", "risks"]
                },
                "key_sentiment_indicators": ["excited", "amazing", "concerned"],
                "sentiment_context": "Mixed feelings about AI technology",
                "mixed_sentiments": ["Positive excitement", "Negative concerns"]
            })
            mock_invoke.return_value = mock_response
            
            result = sentiment_agent.sentiment_analysis_tool(sample_text, "comprehensive")
            
            assert result["overall_sentiment"] is not None
            assert result["confidence_score"] > 0
            assert result["analysis_depth"] == "comprehensive"
    
    @pytest.mark.asyncio
    async def test_tone_analysis_tool(self, sentiment_agent, sample_text):
        """Test tone analysis"""
        with patch.object(sentiment_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "primary_tone": "enthusiastic",
                "secondary_tones": ["concerned", "analytical"],
                "formality_level": "moderate",
                "communication_style": "personal and reflective",
                "tone_consistency": "consistent",
                "tone_shifts": ["From excitement to concern"],
                "audience_appropriateness": "Suitable for general audience",
                "confidence_score": 0.85
            })
            mock_invoke.return_value = mock_response
            
            result = sentiment_agent.tone_analysis_tool(sample_text)
            
            assert result["primary_tone"] is not None
            assert len(result["secondary_tones"]) > 0
            assert result["confidence_score"] > 0
    
    @pytest.mark.asyncio
    async def test_emotion_detection_tool(self, sentiment_agent, sample_text):
        """Test emotion detection"""
        with patch.object(sentiment_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "primary_emotion": "joy",
                "secondary_emotions": ["anticipation", "fear"],
                "emotion_intensities": {
                    "joy": 0.8,
                    "anticipation": 0.6,
                    "fear": 0.4
                },
                "emotional_triggers": ["AI technology", "complex problems"],
                "emotional_expressions": ["excited", "concerned"],
                "emotional_complexity": "complex",
                "emotional_context": "Mixed emotional response to technology",
                "confidence_score": 0.87
            })
            mock_invoke.return_value = mock_response
            
            result = sentiment_agent.emotion_detection_tool(sample_text)
            
            assert result["primary_emotion"] is not None
            assert len(result["secondary_emotions"]) > 0
            assert result["confidence_score"] > 0
    
    @pytest.mark.asyncio
    async def test_bias_detection_tool(self, sentiment_agent, sample_text):
        """Test bias detection"""
        with patch.object(sentiment_agent.llm, 'invoke') as mock_invoke:
            mock_response = Mock()
            mock_response.content = json.dumps({
                "detected_biases": ["optimism bias", "confirmation bias"],
                "bias_intensities": {
                    "optimism bias": 0.6,
                    "confirmation bias": 0.4
                },
                "bias_indicators": ["very excited", "amazing"],
                "objectivity_score": 0.7,
                "fairness_assessment": "Generally fair but shows some bias",
                "bias_impact": "Moderate impact on objectivity",
                "recommendations": ["Consider alternative viewpoints", "Balance positive and negative aspects"],
                "confidence_score": 0.82
            })
            mock_invoke.return_value = mock_response
            
            result = sentiment_agent.bias_detection_tool(sample_text)
            
            assert len(result["detected_biases"]) > 0
            assert result["objectivity_score"] > 0
            assert result["confidence_score"] > 0
    
    @pytest.mark.asyncio
    async def test_execute_method(self, sentiment_agent, sample_text):
        """Test the main execute method"""
        with patch.object(sentiment_agent, 'sentiment_analysis_tool') as mock_tool:
            mock_tool.return_value = {
                "overall_sentiment": "mixed",
                "confidence_score": 0.85
            }
            
            result = await sentiment_agent.execute(sample_text, "Analyze sentiment")
            
            assert result.output is not None
            assert result.confidence > 0
            assert result.agent_type == "sentiment"

class TestAgentServiceIntegration:
    """Integration tests for AgentService with new agents"""
    
    @pytest.fixture
    def agent_service(self):
        """Create an AgentService instance for testing"""
        return AgentService()
    
    @pytest.mark.asyncio
    async def test_execute_single_agent_summarizer(self, agent_service):
        """Test executing summarizer agent through AgentService"""
        with patch.object(agent_service.summarizer_agent, 'execute') as mock_execute:
            mock_execute.return_value = Mock(
                output={"summary": "Test summary"},
                confidence=0.85,
                rationale="Test rationale",
                execution_id="test-123",
                agent_type="summarizer",
                timestamp=datetime.utcnow()
            )
            
            result = await agent_service.execute_single_agent(
                agent_type="summarizer",
                document_content="Test document content",
                goal="Generate summary"
            )
            
            assert result.output is not None
            assert result.confidence > 0
            assert result.agent_type == "summarizer"
    
    @pytest.mark.asyncio
    async def test_execute_single_agent_translator(self, agent_service):
        """Test executing translator agent through AgentService"""
        with patch.object(agent_service.translator_agent, 'execute') as mock_execute:
            mock_execute.return_value = Mock(
                output={"translated_text": "Test translation"},
                confidence=0.88,
                rationale="Test rationale",
                execution_id="test-456",
                agent_type="translator",
                timestamp=datetime.utcnow()
            )
            
            result = await agent_service.execute_single_agent(
                agent_type="translator",
                document_content="Test text to translate",
                goal="Translate text",
                target_language="es"
            )
            
            assert result.output is not None
            assert result.confidence > 0
            assert result.agent_type == "translator"
    
    @pytest.mark.asyncio
    async def test_execute_single_agent_sentiment(self, agent_service):
        """Test executing sentiment agent through AgentService"""
        with patch.object(agent_service.sentiment_agent, 'execute') as mock_execute:
            mock_execute.return_value = Mock(
                output={"overall_sentiment": "positive"},
                confidence=0.82,
                rationale="Test rationale",
                execution_id="test-789",
                agent_type="sentiment",
                timestamp=datetime.utcnow()
            )
            
            result = await agent_service.execute_single_agent(
                agent_type="sentiment",
                document_content="Test text for sentiment analysis",
                goal="Analyze sentiment"
            )
            
            assert result.output is not None
            assert result.confidence > 0
            assert result.agent_type == "sentiment"
    
    def test_get_agent_capabilities_includes_new_agents(self, agent_service):
        """Test that agent capabilities include new agents"""
        capabilities = agent_service.get_agent_capabilities()
        
        assert "summarizer" in capabilities
        assert "translator" in capabilities
        assert "sentiment" in capabilities
        
        assert capabilities["summarizer"]["name"] == "SummarizerAgent"
        assert capabilities["translator"]["name"] == "TranslatorAgent"
        assert capabilities["sentiment"]["name"] == "SentimentAnalysisAgent"

if __name__ == "__main__":
    pytest.main([__file__])
