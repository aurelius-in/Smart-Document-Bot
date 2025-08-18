import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json

from app.services.memory_service import MemoryService


@pytest.fixture
def memory_service():
    """Create a memory service instance for testing"""
    return MemoryService()


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        {
            "id": "doc1",
            "content": "This is a test document about AI and machine learning.",
            "metadata": {
                "source": "test",
                "type": "document",
                "category": "technology"
            }
        },
        {
            "id": "doc2", 
            "content": "Another document about data science and analytics.",
            "metadata": {
                "source": "test",
                "type": "document",
                "category": "technology"
            }
        }
    ]


class TestMemoryService:
    """Test cases for MemoryService"""

    @pytest.mark.asyncio
    async def test_initialization(self, memory_service):
        """Test memory service initialization"""
        assert memory_service is not None
        # Should have fallback ChromaDB client even if Redis fails
        assert memory_service.chroma_client is not None
        assert memory_service.vector_store is not None

    @pytest.mark.asyncio
    async def test_store_and_get_short_term_with_redis(self, memory_service):
        """Test storing and retrieving data from Redis"""
        # Mock Redis client
        mock_redis = AsyncMock()
        memory_service.redis_client = mock_redis
        
        test_data = {"key": "value", "number": 42}
        test_key = "test_key"
        
        # Test storage
        result = await memory_service.store_short_term(test_key, test_data, ttl=3600)
        assert result is True
        mock_redis.setex.assert_called_once()
        
        # Test retrieval
        mock_redis.get.return_value = json.dumps(test_data)
        retrieved_data = await memory_service.get_short_term(test_key)
        assert retrieved_data == test_data
        mock_redis.get.assert_called_once_with(test_key)

    @pytest.mark.asyncio
    async def test_store_and_get_short_term_without_redis(self, memory_service):
        """Test storing and retrieving data without Redis (fallback)"""
        memory_service.redis_client = None
        
        test_data = {"key": "value", "number": 42}
        test_key = "test_key"
        
        # Test storage (should succeed with fallback)
        result = await memory_service.store_short_term(test_key, test_data, ttl=3600)
        assert result is True
        
        # Test retrieval (should return None without Redis)
        retrieved_data = await memory_service.get_short_term(test_key)
        assert retrieved_data is None

    @pytest.mark.asyncio
    async def test_delete_short_term(self, memory_service):
        """Test deleting data from Redis"""
        mock_redis = AsyncMock()
        memory_service.redis_client = mock_redis
        
        test_key = "test_key"
        result = await memory_service.delete_short_term(test_key)
        
        assert result is True
        mock_redis.delete.assert_called_once_with(test_key)

    @pytest.mark.asyncio
    async def test_store_long_term(self, memory_service, sample_documents):
        """Test storing documents in ChromaDB"""
        # Mock ChromaDB collection
        mock_collection = Mock()
        memory_service.vector_store = mock_collection
        
        result = await memory_service.store_long_term("test_collection", sample_documents)
        
        assert result is True
        mock_collection.add.assert_called_once()
        
        # Verify the call arguments
        call_args = mock_collection.add.call_args
        assert len(call_args[1]['ids']) == 2
        assert len(call_args[1]['documents']) == 2
        assert len(call_args[1]['metadatas']) == 2

    @pytest.mark.asyncio
    async def test_store_long_term_empty_documents(self, memory_service):
        """Test storing empty document list"""
        result = await memory_service.store_long_term("test_collection", [])
        assert result is False

    @pytest.mark.asyncio
    async def test_search_long_term(self, memory_service):
        """Test searching documents in ChromaDB"""
        # Mock ChromaDB collection
        mock_collection = Mock()
        memory_service.vector_store = mock_collection
        
        # Mock search results
        mock_results = {
            'documents': [['Document 1 content', 'Document 2 content']],
            'metadatas': [[{'source': 'test'}, {'source': 'test'}]],
            'distances': [[0.1, 0.2]],
            'ids': [['doc1', 'doc2']]
        }
        mock_collection.query.return_value = mock_results
        
        results = await memory_service.search_long_term("test query", k=2)
        
        assert len(results) == 2
        assert results[0]['content'] == 'Document 1 content'
        assert results[0]['score'] == 0.1
        assert results[0]['id'] == 'doc1'
        
        mock_collection.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_long_term_empty_query(self, memory_service):
        """Test searching with empty query"""
        results = await memory_service.search_long_term("", k=5)
        assert results == []

    @pytest.mark.asyncio
    async def test_store_trace_context(self, memory_service):
        """Test storing trace context"""
        with patch.object(memory_service, 'store_short_term') as mock_store:
            mock_store.return_value = True
            
            trace_id = "trace123"
            context = {"step": 1, "agent": "classifier"}
            
            result = await memory_service.store_trace_context(trace_id, context)
            
            assert result is True
            mock_store.assert_called_once_with(f"trace:{trace_id}", context, ttl=7200)

    @pytest.mark.asyncio
    async def test_get_trace_context(self, memory_service):
        """Test retrieving trace context"""
        with patch.object(memory_service, 'get_short_term') as mock_get:
            mock_get.return_value = {"step": 1, "agent": "classifier"}
            
            trace_id = "trace123"
            result = await memory_service.get_trace_context(trace_id)
            
            assert result == {"step": 1, "agent": "classifier"}
            mock_get.assert_called_once_with(f"trace:{trace_id}")

    @pytest.mark.asyncio
    async def test_store_agent_memory(self, memory_service):
        """Test storing agent memory"""
        with patch.object(memory_service, 'store_long_term') as mock_store:
            mock_store.return_value = True
            
            agent_id = "agent123"
            memory_data = {"action": "classify", "confidence": 0.95}
            
            result = await memory_service.store_agent_memory(agent_id, memory_data, "episodic")
            
            assert result is True
            mock_store.assert_called_once()
            
            # Verify the memory document structure
            call_args = mock_store.call_args
            memory_doc = call_args[0][1][0]  # First document in the list
            assert memory_doc['metadata']['agent_id'] == agent_id
            assert memory_doc['metadata']['memory_type'] == 'episodic'
            assert 'data_hash' in memory_doc['metadata']

    @pytest.mark.asyncio
    async def test_search_agent_memory(self, memory_service):
        """Test searching agent memory"""
        with patch.object(memory_service, 'search_long_term') as mock_search:
            mock_search.return_value = [
                {
                    "content": '{"action": "classify", "confidence": 0.95}',
                    "metadata": {"agent_id": "agent123", "memory_type": "episodic"},
                    "score": 0.8
                }
            ]
            
            agent_id = "agent123"
            results = await memory_service.search_agent_memory(agent_id, "classify")
            
            assert len(results) == 1
            assert results[0]['memory_data'] == {"action": "classify", "confidence": 0.95}
            assert results[0]['score'] == 0.8
            
            # Verify filter metadata
            mock_search.assert_called_once()
            call_args = mock_search.call_args
            assert call_args[1]['filter_metadata'] == {"agent_id": agent_id}

    @pytest.mark.asyncio
    async def test_store_document_embeddings(self, memory_service):
        """Test storing document embeddings"""
        with patch.object(memory_service, 'store_long_term') as mock_store:
            mock_store.return_value = True
            
            document_id = "doc123"
            text_chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]
            metadata = {"type": "contract", "domain": "legal"}
            
            result = await memory_service.store_document_embeddings(document_id, text_chunks, metadata)
            
            assert result is True
            mock_store.assert_called_once()
            
            # Verify document structure
            call_args = mock_store.call_args
            documents = call_args[0][1]  # Documents list
            assert len(documents) == 3
            
            for i, doc in enumerate(documents):
                assert doc['id'] == f"{document_id}_chunk_{i}"
                assert doc['content'] == text_chunks[i]
                assert doc['metadata']['document_id'] == document_id
                assert doc['metadata']['chunk_index'] == i
                assert doc['metadata']['type'] == "contract"

    @pytest.mark.asyncio
    async def test_search_similar_documents(self, memory_service):
        """Test searching similar documents"""
        with patch.object(memory_service, 'search_long_term') as mock_search:
            mock_search.return_value = [
                {
                    "content": "Similar document content",
                    "metadata": {"document_type": "contract"},
                    "score": 0.85
                }
            ]
            
            results = await memory_service.search_similar_documents("contract terms", "contract")
            
            assert len(results) == 1
            assert results[0]['content'] == "Similar document content"
            
            # Verify filter metadata
            mock_search.assert_called_once()
            call_args = mock_search.call_args
            assert call_args[1]['filter_metadata'] == {"document_type": "contract"}

    @pytest.mark.asyncio
    async def test_get_collection_stats(self, memory_service):
        """Test getting collection statistics"""
        # Mock ChromaDB collection
        mock_collection = Mock()
        mock_collection.count.return_value = 150
        memory_service.vector_store = mock_collection
        
        stats = await memory_service.get_collection_stats("test_collection")
        
        assert stats['collection_name'] == "test_collection"
        assert stats['document_count'] == 150
        assert stats['status'] == "active"
        
        mock_collection.count.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_collection_stats_no_vector_store(self, memory_service):
        """Test getting collection stats without vector store"""
        memory_service.vector_store = None
        
        stats = await memory_service.get_collection_stats("test_collection")
        
        assert stats['collection_name'] == "test_collection"
        assert stats['document_count'] == 0
        assert stats['status'] == "inactive"

    @pytest.mark.asyncio
    async def test_cleanup_expired_data(self, memory_service):
        """Test cleaning up expired data"""
        # Mock Redis client
        mock_redis = AsyncMock()
        memory_service.redis_client = mock_redis
        
        cleaned_count = await memory_service.cleanup_expired_data(max_age_hours=24)
        
        assert cleaned_count == 0  # Simplified implementation returns 0

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, memory_service):
        """Test health check with healthy services"""
        # Mock Redis client
        mock_redis = AsyncMock()
        memory_service.redis_client = mock_redis
        
        # Mock ChromaDB collection
        mock_collection = Mock()
        mock_collection.count.return_value = 100
        memory_service.vector_store = mock_collection
        
        health = await memory_service.health_check()
        
        assert health['redis'] == 'healthy'
        assert health['chromadb'] == 'healthy'
        assert health['overall'] == 'healthy'

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_redis(self, memory_service):
        """Test health check with unhealthy Redis"""
        # Mock Redis client that fails
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Connection failed")
        memory_service.redis_client = mock_redis
        
        # Mock ChromaDB collection
        mock_collection = Mock()
        mock_collection.count.return_value = 100
        memory_service.vector_store = mock_collection
        
        health = await memory_service.health_check()
        
        assert health['redis'] == 'unhealthy'
        assert health['chromadb'] == 'healthy'
        assert health['overall'] == 'unhealthy'

    @pytest.mark.asyncio
    async def test_health_check_no_redis(self, memory_service):
        """Test health check without Redis configured"""
        memory_service.redis_client = None
        
        # Mock ChromaDB collection
        mock_collection = Mock()
        mock_collection.count.return_value = 100
        memory_service.vector_store = mock_collection
        
        health = await memory_service.health_check()
        
        assert health['redis'] == 'not_configured'
        assert health['chromadb'] == 'healthy'
        assert health['overall'] == 'healthy'

    @pytest.mark.asyncio
    async def test_health_check_error(self, memory_service):
        """Test health check with error"""
        # Mock ChromaDB collection that fails
        mock_collection = Mock()
        mock_collection.count.side_effect = Exception("Database error")
        memory_service.vector_store = mock_collection
        
        health = await memory_service.health_check()
        
        assert health['redis'] == 'unknown'
        assert health['chromadb'] == 'unhealthy'
        assert health['overall'] == 'unhealthy'


class TestMemoryServiceIntegration:
    """Integration tests for MemoryService"""

    @pytest.mark.asyncio
    async def test_full_workflow(self, memory_service):
        """Test complete workflow: store, search, retrieve"""
        # This test would require actual Redis and ChromaDB instances
        # For now, we'll test the workflow with mocked services
        
        with patch.object(memory_service, 'store_short_term') as mock_store, \
             patch.object(memory_service, 'get_short_term') as mock_get, \
             patch.object(memory_service, 'store_long_term') as mock_store_long, \
             patch.object(memory_service, 'search_long_term') as mock_search:
            
            # Setup mocks
            mock_store.return_value = True
            mock_get.return_value = {"test": "data"}
            mock_store_long.return_value = True
            mock_search.return_value = [{"content": "test", "score": 0.8}]
            
            # Test workflow
            # 1. Store trace context
            trace_id = "workflow_test"
            context = {"step": 1, "data": "test"}
            await memory_service.store_trace_context(trace_id, context)
            
            # 2. Store documents
            docs = [{"id": "doc1", "content": "test document"}]
            await memory_service.store_long_term("test", docs)
            
            # 3. Search documents
            results = await memory_service.search_long_term("test")
            
            # 4. Retrieve trace context
            retrieved_context = await memory_service.get_trace_context(trace_id)
            
            # Verify all operations were called
            assert mock_store.called
            assert mock_store_long.called
            assert mock_search.called
            assert mock_get.called
            assert retrieved_context == {"test": "data"}
            assert len(results) == 1
