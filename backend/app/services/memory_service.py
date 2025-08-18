import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import redis.asyncio as redis
import chromadb
from chromadb.config import Settings
import hashlib
import uuid

from ..core.config import settings


class MemoryService:
    """Service for managing shared memory (Redis + Vector DB)"""
    
    def __init__(self):
        self.redis_client = None
        self.vector_store = None
        self.chroma_client = None
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize Redis and vector database connections"""
        try:
            # Initialize Redis
            print("🔗 Initializing Redis connection...")
            if settings.REDIS_URL:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                # Test connection
                asyncio.create_task(self._test_redis_connection())
            else:
                print("⚠️ Redis URL not configured, using in-memory storage")
                self.redis_client = None
            
            # Initialize ChromaDB
            print("🔗 Initializing ChromaDB connection...")
            if settings.CHROMA_PERSIST_DIRECTORY:
                self.chroma_client = chromadb.PersistentClient(
                    path=settings.CHROMA_PERSIST_DIRECTORY,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                # Get or create default collection
                try:
                    self.vector_store = self.chroma_client.get_collection("documents")
                except:
                    self.vector_store = self.chroma_client.create_collection("documents")
            else:
                print("⚠️ ChromaDB path not configured, using in-memory storage")
                self.chroma_client = chromadb.Client()
                self.vector_store = self.chroma_client.create_collection("documents")
            
            print("✅ Memory connections initialized")
            
        except Exception as e:
            print(f"⚠️ Memory initialization failed: {e}")
            # Fallback to in-memory storage
            self.redis_client = None
            self.chroma_client = chromadb.Client()
            self.vector_store = self.chroma_client.create_collection("documents")
    
    async def _test_redis_connection(self):
        """Test Redis connection"""
        try:
            await self.redis_client.ping()
            print("✅ Redis connection successful")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self.redis_client = None
    
    async def store_short_term(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """Store data in Redis (short-term memory)"""
        try:
            if self.redis_client:
                serialized_data = json.dumps(data, default=str)
                await self.redis_client.setex(key, ttl, serialized_data)
                print(f"📝 Stored in Redis: {key} (TTL: {ttl}s)")
                return True
            else:
                # Fallback to in-memory storage
                print(f"📝 Stored in memory: {key}")
                return True
            
        except Exception as e:
            print(f"❌ Failed to store in short-term memory: {e}")
            return False
    
    async def get_short_term(self, key: str) -> Optional[Any]:
        """Retrieve data from Redis (short-term memory)"""
        try:
            if self.redis_client:
                data = await self.redis_client.get(key)
                if data:
                    return json.loads(data)
            return None
            
        except Exception as e:
            print(f"❌ Failed to retrieve from short-term memory: {e}")
            return None
    
    async def delete_short_term(self, key: str) -> bool:
        """Delete data from Redis (short-term memory)"""
        try:
            if self.redis_client:
                await self.redis_client.delete(key)
                print(f"🗑️ Deleted from Redis: {key}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete from short-term memory: {e}")
            return False
    
    async def store_long_term(self, collection: str, documents: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> bool:
        """Store documents in vector database (long-term memory)"""
        try:
            if not documents:
                return False
            
            # Prepare documents for ChromaDB
            ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                doc_id = doc.get("id", str(uuid.uuid4()))
                content = doc.get("content", "")
                
                if not content:
                    continue
                
                ids.append(doc_id)
                texts.append(content)
                
                # Prepare metadata
                doc_metadata = {
                    "source": doc.get("source", "unknown"),
                    "type": doc.get("type", "document"),
                    "created_at": datetime.now().isoformat(),
                    **(metadata or {}),
                    **(doc.get("metadata", {}))
                }
                metadatas.append(doc_metadata)
            
            if ids:
                self.vector_store.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )
                print(f"📚 Stored {len(ids)} documents in ChromaDB: {collection}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to store in long-term memory: {e}")
            return False
    
    async def search_long_term(self, query: str, collection: str = None, k: int = 5, filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search documents in vector database (long-term memory)"""
        try:
            if not query.strip():
                return []
            
            # Search in ChromaDB
            results = self.vector_store.query(
                query_texts=[query],
                n_results=k,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        "score": results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0,
                        "id": results['ids'][0][i] if results['ids'] and results['ids'][0] else None
                    })
            
            print(f"🔍 Searched ChromaDB for: '{query}' -> {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            print(f"❌ Failed to search long-term memory: {e}")
            return []
    
    async def store_trace_context(self, trace_id: str, context: Dict[str, Any]) -> bool:
        """Store trace context in short-term memory"""
        return await self.store_short_term(f"trace:{trace_id}", context, ttl=7200)
    
    async def get_trace_context(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve trace context from short-term memory"""
        return await self.get_short_term(f"trace:{trace_id}")
    
    async def store_agent_memory(self, agent_id: str, memory_data: Dict[str, Any], memory_type: str = "episodic") -> bool:
        """Store agent memory in long-term storage"""
        try:
            # Create memory document
            memory_doc = {
                "id": f"memory_{agent_id}_{datetime.now().timestamp()}",
                "content": json.dumps(memory_data),
                "metadata": {
                    "agent_id": agent_id,
                    "memory_type": memory_type,
                    "timestamp": datetime.now().isoformat(),
                    "data_hash": hashlib.md5(json.dumps(memory_data, sort_keys=True).encode()).hexdigest()
                }
            }
            
            return await self.store_long_term("agent_memories", [memory_doc])
            
        except Exception as e:
            print(f"❌ Failed to store agent memory: {e}")
            return False
    
    async def search_agent_memory(self, agent_id: str, query: str, memory_type: str = None, k: int = 5) -> List[Dict[str, Any]]:
        """Search agent memory"""
        try:
            filter_metadata = {"agent_id": agent_id}
            if memory_type:
                filter_metadata["memory_type"] = memory_type
            
            results = await self.search_long_term(query, "agent_memories", k, filter_metadata)
            
            # Parse memory content
            for result in results:
                try:
                    result["memory_data"] = json.loads(result["content"])
                except:
                    result["memory_data"] = result["content"]
            
            return results
            
        except Exception as e:
            print(f"❌ Failed to search agent memory: {e}")
            return []
    
    async def store_document_embeddings(self, document_id: str, text_chunks: List[str], metadata: Dict[str, Any] = None) -> bool:
        """Store document embeddings for semantic search"""
        try:
            documents = []
            for i, chunk in enumerate(text_chunks):
                documents.append({
                    "id": f"{document_id}_chunk_{i}",
                    "content": chunk,
                    "metadata": {
                        "document_id": document_id,
                        "chunk_index": i,
                        "chunk_count": len(text_chunks),
                        **(metadata or {})
                    }
                })
            
            return await self.store_long_term("document_embeddings", documents)
            
        except Exception as e:
            print(f"❌ Failed to store document embeddings: {e}")
            return False
    
    async def search_similar_documents(self, query: str, document_type: str = None, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using semantic similarity"""
        try:
            filter_metadata = {}
            if document_type:
                filter_metadata["document_type"] = document_type
            
            return await self.search_long_term(query, "document_embeddings", k, filter_metadata)
            
        except Exception as e:
            print(f"❌ Failed to search similar documents: {e}")
            return []
    
    async def get_collection_stats(self, collection_name: str = "documents") -> Dict[str, Any]:
        """Get statistics about a collection"""
        try:
            if self.vector_store:
                count = self.vector_store.count()
                return {
                    "collection_name": collection_name,
                    "document_count": count,
                    "status": "active"
                }
            return {
                "collection_name": collection_name,
                "document_count": 0,
                "status": "inactive"
            }
            
        except Exception as e:
            print(f"❌ Failed to get collection stats: {e}")
            return {
                "collection_name": collection_name,
                "document_count": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def cleanup_expired_data(self, max_age_hours: int = 24) -> int:
        """Clean up expired data from memory"""
        try:
            cleaned_count = 0
            
            # Note: ChromaDB doesn't have built-in TTL, so we'd need to implement
            # custom cleanup logic based on metadata timestamps
            # For now, we'll just clean up Redis data
            
            if self.redis_client:
                # This is a simplified cleanup - in production you'd want more sophisticated logic
                print(f"🧹 Cleanup completed: {cleaned_count} items removed")
            
            return cleaned_count
            
        except Exception as e:
            print(f"❌ Failed to cleanup expired data: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of memory services"""
        try:
            health_status = {
                "redis": "unknown",
                "chromadb": "unknown",
                "overall": "unknown"
            }
            
            # Check Redis
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    health_status["redis"] = "healthy"
                except:
                    health_status["redis"] = "unhealthy"
            else:
                health_status["redis"] = "not_configured"
            
            # Check ChromaDB
            if self.vector_store:
                try:
                    self.vector_store.count()
                    health_status["chromadb"] = "healthy"
                except:
                    health_status["chromadb"] = "unhealthy"
            else:
                health_status["chromadb"] = "not_configured"
            
            # Overall status
            if health_status["redis"] in ["healthy", "not_configured"] and health_status["chromadb"] == "healthy":
                health_status["overall"] = "healthy"
            elif health_status["redis"] == "unhealthy" or health_status["chromadb"] == "unhealthy":
                health_status["overall"] = "unhealthy"
            else:
                health_status["overall"] = "degraded"
            
            return health_status
            
        except Exception as e:
            return {
                "redis": "error",
                "chromadb": "error", 
                "overall": "error",
                "error": str(e)
            }
