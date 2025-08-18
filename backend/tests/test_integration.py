import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from ..app.main import app
from ..app.services.agent_service import AgentService
from ..app.models.base import Document, DocumentType
from ..app.agents.orchestrator import OrchestratorAgent
from ..app.agents.ingestion import IngestionAgent
from ..app.agents.classifier import ClassifierAgent
from ..app.agents.entity import EntityAgent
from ..app.agents.risk import RiskAgent
from ..app.agents.qa import QAAgent
from ..app.agents.compare import CompareAgent
from ..app.agents.audit import AuditAgent

client = TestClient(app)

class TestIntegration:
    """Integration tests for the complete Smart Document Bot system"""
    
    @pytest.fixture
    def sample_document(self):
        """Create a sample document for testing"""
        return Document(
            id="test_doc_001",
            filename="sample_contract.pdf",
            content="This is a sample contract between Company A and Company B. The contract includes terms for payment, delivery, and liability. The total value is $100,000 and the contract duration is 12 months.",
            doc_type=DocumentType.CONTRACT,
            metadata={
                "file_size": 1024000,
                "content_type": "application/pdf",
                "uploaded_by": "test@example.com",
                "uploaded_at": datetime.utcnow().isoformat()
            }
        )
    
    @pytest.fixture
    def agent_service(self):
        """Create an agent service instance for testing"""
        return AgentService()
    
    @pytest.mark.asyncio
    async def test_agent_service_initialization(self, agent_service):
        """Test that agent service initializes correctly with all agents"""
        assert agent_service.orchestrator is not None
        assert agent_service.ingestion_agent is not None
        assert agent_service.classifier_agent is not None
        assert agent_service.entity_agent is not None
        assert agent_service.risk_agent is not None
        assert agent_service.qa_agent is not None
        assert agent_service.compare_agent is not None
        assert agent_service.audit_agent is not None
        
        # Test agent capabilities
        capabilities = agent_service.get_agent_capabilities()
        assert "orchestrator" in capabilities
        assert "ingestion" in capabilities
        assert "classifier" in capabilities
        assert "entity" in capabilities
        assert "risk" in capabilities
        assert "qa" in capabilities
        assert "compare" in capabilities
        assert "audit" in capabilities
    
    @pytest.mark.asyncio
    async def test_document_processing_pipeline(self, agent_service, sample_document):
        """Test the complete document processing pipeline"""
        # Test document processing
        result = await agent_service.process_document(
            document=sample_document,
            goal="Analyze document for compliance and risks"
        )
        
        assert result is not None
        assert "processing_id" in result
        assert "status" in result
        assert "confidence" in result
        assert "rationale" in result
        
        # Verify processing history was created
        processing_id = result["processing_id"]
        processing_status = agent_service.get_processing_status(processing_id)
        assert processing_status is not None
        assert processing_status["processing_id"] == processing_id
    
    @pytest.mark.asyncio
    async def test_single_agent_execution(self, agent_service, sample_document):
        """Test individual agent execution"""
        # Test classifier agent
        classifier_result = await agent_service.execute_single_agent(
            agent_type="classifier",
            document=sample_document,
            goal="Classify document type and analyze content"
        )
        
        assert classifier_result is not None
        assert hasattr(classifier_result, 'output')
        assert hasattr(classifier_result, 'confidence')
        assert hasattr(classifier_result, 'rationale')
        
        # Test entity agent
        entity_result = await agent_service.execute_single_agent(
            agent_type="entity",
            document=sample_document,
            goal="Extract named entities and key information"
        )
        
        assert entity_result is not None
        assert hasattr(entity_result, 'output')
        assert hasattr(entity_result, 'confidence')
    
    @pytest.mark.asyncio
    async def test_document_comparison(self, agent_service, sample_document):
        """Test document comparison functionality"""
        # Create a second document for comparison
        document_b = Document(
            id="test_doc_002",
            filename="sample_contract_v2.pdf",
            content="This is a revised contract between Company A and Company B. The contract includes updated terms for payment, delivery, and liability. The total value is $120,000 and the contract duration is 18 months.",
            doc_type=DocumentType.CONTRACT,
            metadata={
                "file_size": 1024000,
                "content_type": "application/pdf",
                "uploaded_by": "test@example.com",
                "uploaded_at": datetime.utcnow().isoformat()
            }
        )
        
        # Test comparison
        comparison_result = await agent_service.compare_documents(
            document_a=sample_document,
            document_b=document_b,
            goal="Compare documents for differences and risk changes"
        )
        
        assert comparison_result is not None
        assert "status" in comparison_result
        assert "result" in comparison_result
        assert "confidence" in comparison_result
    
    @pytest.mark.asyncio
    async def test_audit_trail_generation(self, agent_service, sample_document):
        """Test audit trail generation"""
        # Test audit trail generation
        audit_result = await agent_service.generate_audit_trail(
            document=sample_document,
            processing_history=[]
        )
        
        assert audit_result is not None
        assert "status" in audit_result
        assert "result" in audit_result
        assert "confidence" in audit_result
    
    @pytest.mark.asyncio
    async def test_qa_generation(self, agent_service, sample_document):
        """Test question and answer generation"""
        # Test QA generation
        qa_result = await agent_service.generate_qa(
            document=sample_document,
            goal="Generate questions and answers about the document"
        )
        
        assert qa_result is not None
        assert "status" in qa_result
        assert "result" in qa_result
        assert "confidence" in qa_result
    
    def test_workflow_status_tracking(self, agent_service):
        """Test workflow status tracking"""
        # Test workflow status
        workflow_status = agent_service.get_workflow_status()
        assert workflow_status is not None
        assert "current_stage" in workflow_status
        assert "completed_stages" in workflow_status
        assert "failed_stages" in workflow_status
        assert "total_execution_time" in workflow_status
        assert "progress_percentage" in workflow_status
    
    def test_processing_history_management(self, agent_service):
        """Test processing history management"""
        # Test processing history
        history = agent_service.get_all_processing_history()
        assert isinstance(history, list)
        
        # Test cleanup
        agent_service.cleanup_old_processing_history(max_age_hours=1)
        # Should not raise any exceptions

class TestAPIEndpoints:
    """Test API endpoints integration"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
    
    def test_agent_capabilities_endpoint(self):
        """Test agent capabilities endpoint"""
        response = client.get("/api/v1/agents/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert "orchestrator" in data
        assert "ingestion" in data
        assert "classifier" in data
        assert "entity" in data
        assert "risk" in data
        assert "qa" in data
        assert "compare" in data
        assert "audit" in data
    
    def test_system_status_endpoint(self):
        """Test system status endpoint"""
        response = client.get("/api/v1/system/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "agents" in data
        assert "workflow_status" in data
        assert "processing_history" in data

class TestOrchestratorAgent:
    """Test orchestrator agent functionality"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator agent for testing"""
        return OrchestratorAgent(llm_model="gpt-4")
    
    @pytest.mark.asyncio
    async def test_workflow_planning(self, orchestrator, sample_document):
        """Test workflow planning functionality"""
        # Test workflow planning tool
        planning_tool = orchestrator.get_tool("plan_workflow")
        assert planning_tool is not None
        
        document_info = {
            "type": sample_document.doc_type.value,
            "size": len(sample_document.content),
            "filename": sample_document.filename
        }
        
        workflow_plan = await planning_tool.execute(
            goal="Analyze document for compliance and risks",
            document_info=document_info
        )
        
        assert workflow_plan is not None
        assert "workflow_id" in workflow_plan
        assert "stages" in workflow_plan
        assert "total_estimated_duration" in workflow_plan
        assert "critical_path" in workflow_plan
    
    @pytest.mark.asyncio
    async def test_execution_monitoring(self, orchestrator):
        """Test execution monitoring functionality"""
        # Test execution monitoring tool
        monitoring_tool = orchestrator.get_tool("monitor_execution")
        assert monitoring_tool is not None
        
        workflow_plan = {
            "workflow_id": "test_wf_001",
            "stages": [
                {
                    "stage_id": "stage_1",
                    "stage_name": "Document Ingestion",
                    "agent_type": "IngestionAgent",
                    "priority": "HIGH"
                }
            ],
            "total_estimated_duration": 180
        }
        
        execution_status = {
            "completed_stages": ["stage_1"],
            "failed_stages": [],
            "execution_history": []
        }
        
        monitoring_result = await monitoring_tool.execute(
            workflow_plan=workflow_plan,
            execution_status=execution_status
        )
        
        assert monitoring_result is not None
        assert "overall_status" in monitoring_result
        assert "performance_score" in monitoring_result
        assert "monitoring_checks" in monitoring_result

class TestAgentTools:
    """Test individual agent tools"""
    
    @pytest.mark.asyncio
    async def test_classifier_tools(self, sample_document):
        """Test classifier agent tools"""
        classifier = ClassifierAgent(llm_model="gpt-4")
        
        # Test content analysis tool
        content_tool = classifier.get_tool("content_analysis")
        assert content_tool is not None
        
        content_result = await content_tool.execute(
            document_content=sample_document.content,
            document_type=sample_document.doc_type.value
        )
        
        assert content_result is not None
        assert "word_count" in content_result
        assert "character_count" in content_result
        assert "paragraph_count" in content_result
        assert "structure_score" in content_result
    
    @pytest.mark.asyncio
    async def test_entity_tools(self, sample_document):
        """Test entity agent tools"""
        entity_agent = EntityAgent(llm_model="gpt-4")
        
        # Test named entity recognition tool
        ner_tool = entity_agent.get_tool("named_entity_recognition")
        assert ner_tool is not None
        
        ner_result = await ner_tool.execute(
            document_content=sample_document.content,
            document_type=sample_document.doc_type.value
        )
        
        assert ner_result is not None
        assert "entities" in ner_result
        assert "confidence" in ner_result
    
    @pytest.mark.asyncio
    async def test_risk_tools(self, sample_document):
        """Test risk agent tools"""
        risk_agent = RiskAgent(llm_model="gpt-4")
        
        # Test compliance risk analysis tool
        compliance_tool = risk_agent.get_tool("compliance_risk_analysis")
        assert compliance_tool is not None
        
        compliance_result = await compliance_tool.execute(
            document_content=sample_document.content,
            document_type=sample_document.doc_type.value,
            extracted_entities=[]
        )
        
        assert compliance_result is not None
        assert "compliance_risks" in compliance_result
        assert "overall_risk_score" in compliance_result

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_document_processing(self, agent_service):
        """Test processing with invalid document"""
        # Test with None document
        result = await agent_service.process_document(
            document=None,
            goal="Test processing"
        )
        
        assert result is not None
        assert result["status"] == "failed"
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_invalid_agent_type(self, agent_service, sample_document):
        """Test execution with invalid agent type"""
        result = await agent_service.execute_single_agent(
            agent_type="invalid_agent",
            document=sample_document,
            goal="Test execution"
        )
        
        assert result is not None
        assert result.confidence == 0.0
        assert "error" in result.rationale.lower()
    
    def test_workflow_status_without_execution(self, agent_service):
        """Test workflow status without any execution"""
        workflow_status = agent_service.get_workflow_status()
        assert workflow_status is not None
        assert workflow_status["current_stage"] == "planning"
        assert workflow_status["progress_percentage"] == 0.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
