import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import redis.asyncio as redis
import chromadb
from chromadb.config import Settings
import hashlib
import uuid

from ..core.config import settings
from ..core.monitoring import get_monitor

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing shared memory (Redis + Vector DB)"""
    
    def __init__(self):
        self.monitor = get_monitor()
        self.redis_client = None
        self.vector_store = None
        self.chroma_client = None
        self.is_initialized = False
        
        # In-memory fallback storage
        self._memory_storage = {}
    
    async def initialize(self) -> None:
        """Initialize Redis and vector database connections"""
        try:
            logger.info("Initializing MemoryService...")
            
            # Initialize Redis
            await self._initialize_redis()
            
            # Initialize ChromaDB
            await self._initialize_chromadb()
            
            self.is_initialized = True
            logger.info("MemoryService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MemoryService: {e}")
            # Fallback to in-memory storage
            self._setup_fallback_storage()
            raise
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            if settings.REDIS_URL:
                logger.info("Initializing Redis connection...")
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    max_connections=settings.REDIS_MAX_CONNECTIONS
                )
                
                # Test connection
                await self.redis_client.ping()
                logger.info("Redis connection successful")
            else:
                logger.warning("Redis URL not configured, using in-memory storage")
                self.redis_client = None
                
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            self.redis_client = None
    
    async def _initialize_chromadb(self) -> None:
        """Initialize ChromaDB connection"""
        try:
            logger.info("Initializing ChromaDB connection...")
            
            if settings.CHROMA_PERSIST_DIRECTORY:
                self.chroma_client = chromadb.PersistentClient(
                    path=settings.CHROMA_PERSIST_DIRECTORY,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
            else:
                logger.warning("ChromaDB path not configured, using in-memory storage")
                self.chroma_client = chromadb.Client()
            
            # Get or create default collection
            try:
                self.vector_store = self.chroma_client.get_collection(settings.CHROMA_COLLECTION_NAME)
                logger.info(f"Using existing ChromaDB collection: {settings.CHROMA_COLLECTION_NAME}")
            except Exception:
                self.vector_store = self.chroma_client.create_collection(settings.CHROMA_COLLECTION_NAME)
                logger.info(f"Created new ChromaDB collection: {settings.CHROMA_COLLECTION_NAME}")
            
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            self._setup_fallback_storage()
    
    def _setup_fallback_storage(self) -> None:
        """Setup fallback in-memory storage"""
        logger.info("Setting up fallback in-memory storage")
        self.chroma_client = chromadb.Client()
        self.vector_store = self.chroma_client.create_collection("documents")
    
    async def store_short_term(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """Store data in Redis (short-term memory)"""
        if not self.is_initialized:
            raise RuntimeError("MemoryService not initialized. Call initialize() first.")
        
        try:
            if self.redis_client:
                serialized_data = json.dumps(data, default=str)
                await self.redis_client.setex(key, ttl, serialized_data)
                logger.debug(f"Stored in Redis: {key} (TTL: {ttl}s)")
                return True
            else:
                # Fallback to in-memory storage
                self._memory_storage[key] = {
                    "data": data,
                    "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
                }
                logger.debug(f"Stored in memory: {key}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to store in short-term memory: {e}")
            return False
    
    async def get_short_term(self, key: str) -> Optional[Any]:
        """Retrieve data from Redis (short-term memory)"""
        if not self.is_initialized:
            raise RuntimeError("MemoryService not initialized. Call initialize() first.")
        
        try:
            if self.redis_client:
                data = await self.redis_client.get(key)
                if data:
                    return json.loads(data)
            else:
                # Check in-memory storage
                if key in self._memory_storage:
                    item = self._memory_storage[key]
                    if datetime.utcnow() < item["expires_at"]:
                        return item["data"]
                    else:
                        # Remove expired item
                        del self._memory_storage[key]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve from short-term memory: {e}")
            return None
    
    async def delete_short_term(self, key: str) -> bool:
        """Delete data from Redis (short-term memory)"""
        if not self.is_initialized:
            raise RuntimeError("MemoryService not initialized. Call initialize() first.")
        
        try:
            if self.redis_client:
                await self.redis_client.delete(key)
                logger.debug(f"Deleted from Redis: {key}")
            else:
                # Remove from in-memory storage
                if key in self._memory_storage:
                    del self._memory_storage[key]
                    logger.debug(f"Deleted from memory: {key}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete from short-term memory: {e}")
            return False
    
    async def store_long_term(self, collection: str, documents: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> bool:
        """Store documents in vector database (long-term memory)"""
        if not self.is_initialized:
            raise RuntimeError("MemoryService not initialized. Call initialize() first.")
        
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
                    "collection": collection,
                    "created_at": datetime.utcnow().isoformat(),
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
                logger.info(f"Stored {len(ids)} documents in ChromaDB collection: {collection}")
                
                # Record metrics
                self.monitor.record_performance_metric(
                    "documents_stored",
                    len(ids),
                    {"collection": collection}
                )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to store in long-term memory: {e}")
            return False
    
    async def search_long_term(self, query: str, collection: str = None, k: int = 5, filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search documents in vector database (long-term memory)"""
        if not self.is_initialized:
            raise RuntimeError("MemoryService not initialized. Call initialize() first.")
        
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
            
            logger.debug(f"Searched ChromaDB for: '{query}' -> {len(formatted_results)} results")
            
            # Record metrics
            self.monitor.record_performance_metric(
                "search_results",
                len(formatted_results),
                {"collection": collection or "default"}
            )
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search long-term memory: {e}")
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
                "id": f"memory_{agent_id}_{datetime.utcnow().timestamp()}",
                "content": json.dumps(memory_data),
                "metadata": {
                    "agent_id": agent_id,
                    "memory_type": memory_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data_hash": hashlib.md5(json.dumps(memory_data, sort_keys=True).encode()).hexdigest()
                }
            }
            
            return await self.store_long_term("agent_memories", [memory_doc])
            
        except Exception as e:
            logger.error(f"Failed to store agent memory: {e}")
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
            logger.error(f"Failed to search agent memory: {e}")
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
            logger.error(f"Failed to store document embeddings: {e}")
            return False
    
    async def search_similar_documents(self, query: str, document_type: str = None, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using semantic similarity"""
        try:
            filter_metadata = {}
            if document_type:
                filter_metadata["document_type"] = document_type
            
            return await self.search_long_term(query, "document_embeddings", k, filter_metadata)
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            return []
    
    async def get_collection_stats(self, collection_name: str = None) -> Dict[str, Any]:
        """Get statistics about collections"""
        if not self.is_initialized:
            raise RuntimeError("MemoryService not initialized. Call initialize() first.")
        
        try:
            collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
            
            if self.vector_store:
                count = self.vector_store.count()
                return {
                    "collection_name": collection_name,
                    "document_count": count,
                    "status": "active",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "collection_name": collection_name,
                "document_count": 0,
                "status": "inactive",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "collection_name": collection_name,
                "document_count": 0,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def cleanup_expired_data(self, max_age_hours: int = 24) -> int:
        """Clean up expired data from memory"""
        if not self.is_initialized:
            raise RuntimeError("MemoryService not initialized. Call initialize() first.")
        
        try:
            cleaned_count = 0
            
            # Clean up in-memory storage
            current_time = datetime.utcnow()
            expired_keys = []
            
            for key, item in self._memory_storage.items():
                if current_time > item["expires_at"]:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._memory_storage[key]
                cleaned_count += 1
            
            # Note: ChromaDB doesn't have built-in TTL, so we'd need to implement
            # custom cleanup logic based on metadata timestamps
            # For now, we'll just clean up Redis data
            
            logger.info(f"Cleanup completed: {cleaned_count} items removed")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of memory services"""
        if not self.is_initialized:
            return {
                "redis": "not_initialized",
                "chromadb": "not_initialized",
                "overall": "not_initialized"
            }
        
        try:
            health_status = {
                "redis": "unknown",
                "chromadb": "unknown",
                "overall": "unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check Redis
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    health_status["redis"] = "healthy"
                except Exception as e:
                    logger.error(f"Redis health check failed: {e}")
                    health_status["redis"] = "unhealthy"
            else:
                health_status["redis"] = "not_configured"
            
            # Check ChromaDB
            if self.vector_store:
                try:
                    self.vector_store.count()
                    health_status["chromadb"] = "healthy"
                except Exception as e:
                    logger.error(f"ChromaDB health check failed: {e}")
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
            logger.error(f"Memory service health check failed: {e}")
            return {
                "redis": "error",
                "chromadb": "error", 
                "overall": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        return {
            "initialized": self.is_initialized,
            "redis_configured": self.redis_client is not None,
            "chromadb_configured": self.vector_store is not None,
            "health": await self.health_check(),
            "collections": await self.get_collection_stats(),
            "memory_storage_size": len(self._memory_storage)
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources and connections"""
        try:
            logger.info("Cleaning up MemoryService...")
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis connection closed")
            
            # Clear in-memory storage
            self._memory_storage.clear()
            
            # Clear ChromaDB references
            self.vector_store = None
            self.chroma_client = None
            
            self.is_initialized = False
            logger.info("MemoryService cleanup completed")
            
        except Exception as e:
            logger.error(f"MemoryService cleanup failed: {e}")
            raise
