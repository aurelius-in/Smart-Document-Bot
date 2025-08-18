import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json
from fastapi.testclient import TestClient

from app.main import app
from app.services.agent_service import AgentService
from app.agents.summarizer import SummarizerAgent
from app.agents.translator import TranslatorAgent
from app.agents.sentiment import SentimentAnalysisAgent

client = TestClient(app)

class TestUnifiedAgentsAPI:
    """Test cases for unified agents API endpoints"""
    
    @pytest.fixture
    def mock_agent_service(self):
        """Create a mock agent service for testing"""
        with patch('app.main.get_agent_service') as mock:
            service = Mock(spec=AgentService)
            
            # Mock agent instances
            service.summarizer_agent = Mock(spec=SummarizerAgent)
            service.translator_agent = Mock(spec=TranslatorAgent)
            service.sentiment_agent = Mock(spec=SentimentAnalysisAgent)
            
            # Mock methods
            service.execute_single_agent = AsyncMock()
            service.get_agent_capabilities = Mock()
            service.get_workflow_status = Mock()
            service.get_all_processing_history = Mock()
            service.cleanup_old_processing_history = AsyncMock()
            service.log_agent_trace = AsyncMock()
            
            mock.return_value = service
            yield service
    
    def test_execute_agent_success(self, mock_agent_service):
        """Test successful agent execution"""
        # Mock the agent execution result
        mock_result = Mock()
        mock_result.execution_id = "test-123"
        mock_result.output = {"summary": "Test summary"}
        mock_result.confidence = 0.85
        mock_result.rationale = "Test rationale"
        
        mock_agent_service.execute_single_agent.return_value = mock_result
        
        # Test request
        request_data = {
            "agent_type": "summarizer",
            "document_content": "Test document content",
            "goal": "Generate summary",
            "parameters": {"summary_type": "abstractive"}
        }
        
        response = client.post("/api/v1/agents/execute", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["execution_id"] == "test-123"
        assert data["agent_type"] == "summarizer"
        assert data["confidence"] == 0.85
        
        # Verify the service was called correctly
        mock_agent_service.execute_single_agent.assert_called_once()
        call_args = mock_agent_service.execute_single_agent.call_args
        assert call_args[1]["agent_type"] == "summarizer"
        assert call_args[1]["document_content"] == "Test document content"
        assert call_args[1]["goal"] == "Generate summary"
    
    def test_batch_execute_agents_success(self, mock_agent_service):
        """Test successful batch agent execution"""
        # Mock the agent execution results
        mock_result1 = Mock()
        mock_result1.execution_id = "test-1"
        mock_result1.output = {"summary": "Summary 1"}
        mock_result1.confidence = 0.85
        mock_result1.rationale = "Rationale 1"
        
        mock_result2 = Mock()
        mock_result2.execution_id = "test-2"
        mock_result2.output = {"translation": "Translation 2"}
        mock_result2.confidence = 0.90
        mock_result2.rationale = "Rationale 2"
        
        mock_agent_service.execute_single_agent.side_effect = [mock_result1, mock_result2]
        
        # Test request
        request_data = {
            "executions": [
                {
                    "agent_type": "summarizer",
                    "document_content": "Content 1",
                    "goal": "Summarize",
                    "parameters": {}
                },
                {
                    "agent_type": "translator",
                    "document_content": "Content 2",
                    "goal": "Translate",
                    "parameters": {"target_language": "es"}
                }
            ]
        }
        
        response = client.post("/api/v1/agents/batch-execute", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["batch_id"] == "batch_2"
        assert len(data["results"]) == 2
        
        # Verify results
        assert data["results"][0]["agent_type"] == "summarizer"
        assert data["results"][1]["agent_type"] == "translator"
        
        # Verify the service was called twice
        assert mock_agent_service.execute_single_agent.call_count == 2
    
    def test_get_agent_capabilities(self, mock_agent_service):
        """Test getting agent capabilities"""
        # Mock capabilities
        mock_capabilities = {
            "summarizer": {
                "name": "SummarizerAgent",
                "description": "Generates document summaries",
                "capabilities": ["extractive", "abstractive", "executive"]
            },
            "translator": {
                "name": "TranslatorAgent",
                "description": "Translates documents",
                "capabilities": ["translate", "detect_language"]
            }
        }
        
        mock_agent_service.get_agent_capabilities.return_value = mock_capabilities
        
        response = client.get("/api/v1/agents/capabilities")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_agents"] == 2
        assert "summarizer" in data["capabilities"]
        assert "translator" in data["capabilities"]
        
        # Verify enhanced capabilities
        summarizer_cap = data["capabilities"]["summarizer"]
        assert summarizer_cap["status"] == "available"
        assert summarizer_cap["version"] == "1.0.0"
        assert "supported_formats" in summarizer_cap
    
    def test_get_agents_status(self, mock_agent_service):
        """Test getting agents status"""
        # Mock status data
        mock_agent_service.get_workflow_status.return_value = {"status": "idle"}
        mock_agent_service.get_all_processing_history.return_value = [
            {"status": "completed", "timestamp": "2024-01-01T00:00:00Z"},
            {"status": "failed", "timestamp": "2024-01-01T01:00:00Z"},
            {"status": "processing", "timestamp": "2024-01-01T02:00:00Z"}
        ]
        
        response = client.get("/api/v1/agents/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["workflow_status"]["status"] == "idle"
        
        # Verify statistics
        stats = data["agent_statistics"]
        assert stats["total_executions"] == 3
        assert stats["successful_executions"] == 1
        assert stats["failed_executions"] == 1
        assert stats["active_processing"] == 1
    
    def test_execute_agent_capability(self, mock_agent_service):
        """Test executing specific agent capability"""
        # Mock the capability method
        mock_method = Mock()
        mock_method.return_value = {"result": "test result"}
        mock_agent_service.summarizer_agent.extractive_summary_tool = mock_method
        
        request_data = {
            "agent_type": "summarizer",
            "capability": "extractive",
            "parameters": {"summary_length": "medium"}
        }
        
        response = client.post("/api/v1/agents/capability", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["agent_type"] == "summarizer"
        assert data["capability"] == "extractive"
        assert data["result"]["result"] == "test result"
        
        # Verify the method was called
        mock_method.assert_called_once_with(summary_length="medium")
    
    def test_execute_agent_capability_unknown_agent(self, mock_agent_service):
        """Test executing capability with unknown agent type"""
        request_data = {
            "agent_type": "unknown_agent",
            "capability": "test",
            "parameters": {}
        }
        
        response = client.post("/api/v1/agents/capability", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Unknown agent type" in data["detail"]
    
    def test_execute_agent_capability_unknown_capability(self, mock_agent_service):
        """Test executing unknown capability"""
        request_data = {
            "agent_type": "summarizer",
            "capability": "unknown_capability",
            "parameters": {}
        }
        
        response = client.post("/api/v1/agents/capability", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Unknown capability" in data["detail"]
    
    def test_get_agents_health(self):
        """Test getting agents health"""
        response = client.get("/api/v1/agents/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["health"]["status"] == "healthy"
        assert "agents" in data["health"]
        
        # Verify all agents are listed
        agents = data["health"]["agents"]
        expected_agents = ["summarizer", "translator", "sentiment", "classifier", 
                          "entity", "risk", "qa", "compare", "audit"]
        for agent in expected_agents:
            assert agent in agents
            assert agents[agent] == "healthy"
    
    def test_cleanup_old_executions(self, mock_agent_service):
        """Test cleaning up old executions"""
        response = client.delete("/api/v1/agents/cleanup?max_age_hours=48")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Cleaned up executions older than 48 hours" in data["message"]
        
        # Verify cleanup was called
        mock_agent_service.cleanup_old_processing_history.assert_called_once_with(48)
    
    def test_execute_agent_error_handling(self, mock_agent_service):
        """Test error handling in agent execution"""
        # Mock an exception
        mock_agent_service.execute_single_agent.side_effect = Exception("Test error")
        
        request_data = {
            "agent_type": "summarizer",
            "document_content": "Test content",
            "goal": "Test goal"
        }
        
        response = client.post("/api/v1/agents/execute", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "Agent execution failed" in data["detail"]
    
    def test_batch_execute_agents_error_handling(self, mock_agent_service):
        """Test error handling in batch execution"""
        # Mock an exception on second execution
        mock_result1 = Mock()
        mock_result1.execution_id = "test-1"
        mock_result1.output = {"result": "success"}
        mock_result1.confidence = 0.85
        mock_result1.rationale = "Success"
        
        mock_agent_service.execute_single_agent.side_effect = [
            mock_result1,
            Exception("Test error")
        ]
        
        request_data = {
            "executions": [
                {
                    "agent_type": "summarizer",
                    "document_content": "Content 1",
                    "goal": "Summarize"
                },
                {
                    "agent_type": "translator",
                    "document_content": "Content 2",
                    "goal": "Translate"
                }
            ]
        }
        
        response = client.post("/api/v1/agents/batch-execute", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "Batch execution failed" in data["detail"]
    
    def test_invalid_request_data(self):
        """Test handling of invalid request data"""
        # Test missing required fields
        request_data = {
            "agent_type": "summarizer"
            # Missing document_content and goal
        }
        
        response = client.post("/api/v1/agents/execute", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_agent_execution_with_parameters(self, mock_agent_service):
        """Test agent execution with various parameters"""
        mock_result = Mock()
        mock_result.execution_id = "test-params"
        mock_result.output = {"result": "parameterized result"}
        mock_result.confidence = 0.95
        mock_result.rationale = "Parameters applied"
        
        mock_agent_service.execute_single_agent.return_value = mock_result
        
        request_data = {
            "agent_type": "sentiment",
            "document_content": "I love this product!",
            "goal": "Analyze sentiment",
            "parameters": {
                "analysis_depth": "comprehensive",
                "include_emotions": True,
                "detect_bias": True
            }
        }
        
        response = client.post("/api/v1/agents/execute", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["agent_type"] == "sentiment"
        
        # Verify parameters were passed correctly
        call_args = mock_agent_service.execute_single_agent.call_args
        assert call_args[1]["analysis_depth"] == "comprehensive"
        assert call_args[1]["include_emotions"] is True
        assert call_args[1]["detect_bias"] is True

class TestAgentServiceIntegration:
    """Integration tests for AgentService with unified API"""
    
    @pytest.fixture
    def agent_service(self):
        """Create a real AgentService instance for integration testing"""
        return AgentService()
    
    @pytest.mark.asyncio
    async def test_execute_single_agent_integration(self, agent_service):
        """Test integration with real agent service"""
        with patch.object(agent_service.summarizer_agent, 'execute') as mock_execute:
            mock_execute.return_value = Mock(
                output={"summary": "Integration test summary"},
                confidence=0.88,
                rationale="Integration test rationale",
                execution_id="integration-123",
                agent_type="summarizer",
                timestamp=datetime.utcnow()
            )
            
            result = await agent_service.execute_single_agent(
                agent_type="summarizer",
                document_content="Integration test content",
                goal="Test integration"
            )
            
            assert result.output is not None
            assert result.confidence > 0
            assert result.agent_type == "summarizer"
    
    def test_get_agent_capabilities_integration(self, agent_service):
        """Test getting capabilities from real agent service"""
        capabilities = agent_service.get_agent_capabilities()
        
        # Verify all expected agents are present
        expected_agents = [
            "orchestrator", "ingestion", "classifier", "entity", 
            "risk", "qa", "compare", "audit", "summarizer", 
            "translator", "sentiment"
        ]
        
        for agent in expected_agents:
            assert agent in capabilities
            assert "name" in capabilities[agent]
            assert "description" in capabilities[agent]
            assert "capabilities" in capabilities[agent]
    
    @pytest.mark.asyncio
    async def test_cleanup_integration(self, agent_service):
        """Test cleanup functionality integration"""
        # Add some mock processing history
        agent_service.processing_history = {
            "old-1": {
                "processing_id": "old-1",
                "start_time": "2024-01-01T00:00:00Z",
                "status": "completed"
            },
            "new-1": {
                "processing_id": "new-1",
                "start_time": "2024-12-31T23:00:00Z",
                "status": "completed"
            }
        }
        
        # Clean up old executions (older than 1 hour)
        await agent_service.cleanup_old_processing_history(max_age_hours=1)
        
        # Verify old execution was removed
        assert "old-1" not in agent_service.processing_history
        assert "new-1" in agent_service.processing_history

if __name__ == "__main__":
    pytest.main([__file__])
