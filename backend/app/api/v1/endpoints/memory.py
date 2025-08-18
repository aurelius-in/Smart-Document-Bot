from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...services.memory_service import MemoryService

router = APIRouter()


class MemoryStats(BaseModel):
    """Memory statistics model"""
    redis_connected: bool
    chroma_connected: bool
    total_documents: int
    total_embeddings: int
    memory_usage_mb: float
    cache_hit_rate: float
    last_cleanup: str


class SearchRequest(BaseModel):
    """Memory search request model"""
    query: str
    k: int = 5
    filter_metadata: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """Memory search result model"""
    id: str
    content: str
    metadata: Dict[str, Any]
    distance: float
    score: float


class MemoryEntry(BaseModel):
    """Memory entry model"""
    id: str
    content: str
    metadata: Dict[str, Any]
    created_at: str
    last_accessed: str


@router.get("/stats", response_model=MemoryStats)
async def get_memory_stats(
    current_user: dict = Depends(require_permissions(["read"])),
    memory_service: MemoryService = Depends()
):
    """Get memory service statistics"""
    try:
        stats = await memory_service.health_check()
        
        return MemoryStats(
            redis_connected=stats.get("redis_connected", False),
            chroma_connected=stats.get("chroma_connected", False),
            total_documents=stats.get("total_documents", 0),
            total_embeddings=stats.get("total_embeddings", 0),
            memory_usage_mb=stats.get("memory_usage_mb", 0.0),
            cache_hit_rate=stats.get("cache_hit_rate", 0.0),
            last_cleanup=stats.get("last_cleanup", "Never")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[SearchResult])
async def search_memory(
    request: SearchRequest,
    current_user: dict = Depends(require_permissions(["read"])),
    memory_service: MemoryService = Depends()
):
    """Search memory for similar content"""
    try:
        results = await memory_service.search_long_term(
            query=request.query,
            k=request.k,
            filter_metadata=request.filter_metadata
        )
        
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                id=result.get("id", ""),
                content=result.get("content", ""),
                metadata=result.get("metadata", {}),
                distance=result.get("distance", 0.0),
                score=result.get("score", 0.0)
            ))
        
        return search_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=List[MemoryEntry])
async def get_memory_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_permissions(["read"])),
    memory_service: MemoryService = Depends()
):
    """Get documents stored in memory"""
    try:
        # In a real implementation, this would fetch from the memory service
        # For now, return mock data
        mock_documents = [
            {
                "id": "doc_001",
                "content": "Sample document content for contract analysis",
                "metadata": {"type": "contract", "uploaded_by": current_user["email"]},
                "created_at": "2024-01-15T10:30:00Z",
                "last_accessed": "2024-01-15T11:00:00Z"
            },
            {
                "id": "doc_002",
                "content": "Another document for comparison purposes",
                "metadata": {"type": "policy", "uploaded_by": current_user["email"]},
                "created_at": "2024-01-15T10:35:00Z",
                "last_accessed": "2024-01-15T10:45:00Z"
            }
        ]
        
        # Calculate pagination
        total = len(mock_documents)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_docs = mock_documents[start_idx:end_idx]
        
        return [MemoryEntry(**doc) for doc in paginated_docs]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_memory_document(
    document_id: str,
    current_user: dict = Depends(require_permissions(["delete"])),
    memory_service: MemoryService = Depends()
):
    """Delete a document from memory"""
    try:
        # In a real implementation, this would delete from the memory service
        # For now, just return success
        return {"message": f"Document {document_id} deleted from memory"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_memory(
    current_user: dict = Depends(require_permissions(["admin"])),
    memory_service: MemoryService = Depends()
):
    """Clean up expired memory entries (admin only)"""
    try:
        result = await memory_service.cleanup_expired_data()
        return {
            "message": "Memory cleanup completed",
            "cleaned_entries": result.get("cleaned_entries", 0),
            "freed_memory_mb": result.get("freed_memory_mb", 0.0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections")
async def get_memory_collections(
    current_user: dict = Depends(require_permissions(["read"])),
    memory_service: MemoryService = Depends()
):
    """Get memory collections information"""
    try:
        stats = await memory_service.get_collection_stats()
        return {
            "collections": stats.get("collections", []),
            "total_collections": stats.get("total_collections", 0),
            "total_embeddings": stats.get("total_embeddings", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/store")
async def store_in_memory(
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    memory_type: str = "long_term",  # long_term or short_term
    current_user: dict = Depends(require_permissions(["write"])),
    memory_service: MemoryService = Depends()
):
    """Store content in memory"""
    try:
        if memory_type == "long_term":
            result = await memory_service.store_long_term(
                documents=[content],
                metadatas=[metadata or {}]
            )
        else:
            result = await memory_service.store_short_term(
                key=f"user_{current_user['id']}_{len(content)}",
                value=content,
                ttl=3600  # 1 hour
            )
        
        return {
            "message": f"Content stored in {memory_type} memory",
            "stored_id": result.get("id", "unknown")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
