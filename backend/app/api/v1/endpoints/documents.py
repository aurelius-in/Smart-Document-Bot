import os
import shutil
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...core.config import settings
from ...services.agent_service import AgentService

router = APIRouter()


class DocumentInfo(BaseModel):
    """Document information model"""
    id: str
    filename: str
    size: int
    type: str
    status: str
    uploadedAt: str
    processedAt: Optional[str] = None
    metadata: Optional[dict] = None
    extractedText: Optional[str] = None
    entities: Optional[List[dict]] = None
    confidence: Optional[float] = None


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    fileId: str
    filename: str
    size: int
    status: str
    message: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[DocumentInfo]
    pagination: dict


# Mock document storage - in production, this would be a database
DOCUMENT_STORE = {}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    process_immediately: bool = Form(False),
    goal: Optional[str] = Form("Analyze document for compliance and risks"),
    current_user: dict = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """Upload and optionally process a document"""
    
    # Validate file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
        )
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size {file.size} exceeds maximum allowed size of {settings.MAX_FILE_SIZE}"
        )
    
    try:
        # Create unique document ID
        document_id = str(uuid.uuid4())
        filename = f"{document_id}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create document record
        document_info = {
            "id": document_id,
            "filename": file.filename,
            "size": file_size,
            "type": file_extension,
            "status": "uploaded",
            "uploadedAt": datetime.utcnow().isoformat(),
            "processedAt": None,
            "metadata": {
                "content_type": file.content_type,
                "uploaded_by": current_user["email"],
                "file_path": file_path
            },
            "extractedText": None,
            "entities": None,
            "confidence": None
        }
        
        # Store document info
        DOCUMENT_STORE[document_id] = document_info
        
        # Process document if requested
        if process_immediately:
            try:
                result = await agent_service.process_document(file_path, goal)
                document_info["status"] = "completed"
                document_info["processedAt"] = datetime.utcnow().isoformat()
                document_info["extractedText"] = result.get("extracted_text", "")
                document_info["entities"] = result.get("entities", [])
                document_info["confidence"] = result.get("confidence", 0.0)
                document_info["metadata"]["trace_id"] = result.get("trace_id")
            except Exception as e:
                document_info["status"] = "error"
                document_info["metadata"]["error"] = str(e)
        
        return DocumentUploadResponse(
            fileId=document_id,
            filename=file.filename,
            size=file_size,
            status=document_info["status"],
            message="Document uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/", response_model=PaginatedResponse)
async def get_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of documents"""
    try:
        # Get all documents
        documents = list(DOCUMENT_STORE.values())
        
        # Calculate pagination
        total = len(documents)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_docs = documents[start_idx:end_idx]
        
        # Convert to DocumentInfo models
        document_infos = [
            DocumentInfo(
                id=doc["id"],
                filename=doc["filename"],
                size=doc["size"],
                type=doc["type"],
                status=doc["status"],
                uploadedAt=doc["uploadedAt"],
                processedAt=doc["processedAt"],
                metadata=doc["metadata"],
                extractedText=doc["extractedText"],
                entities=doc["entities"],
                confidence=doc["confidence"]
            )
            for doc in paginated_docs
        ]
        
        return PaginatedResponse(
            data=document_infos,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific document by ID"""
    try:
        if document_id not in DOCUMENT_STORE:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = DOCUMENT_STORE[document_id]
        return DocumentInfo(
            id=doc["id"],
            filename=doc["filename"],
            size=doc["size"],
            type=doc["type"],
            status=doc["status"],
            uploadedAt=doc["uploadedAt"],
            processedAt=doc["processedAt"],
            metadata=doc["metadata"],
            extractedText=doc["extractedText"],
            entities=doc["entities"],
            confidence=doc["confidence"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/process")
async def process_document(
    document_id: str,
    goal: str = "Analyze document for compliance and risks",
    current_user: dict = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Process an uploaded document"""
    try:
        if document_id not in DOCUMENT_STORE:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = DOCUMENT_STORE[document_id]
        file_path = doc["metadata"]["file_path"]
        
        # Update status to processing
        doc["status"] = "processing"
        
        # Process document
        result = await agent_service.process_document(file_path, goal)
        
        # Update document info
        doc["status"] = "completed"
        doc["processedAt"] = datetime.utcnow().isoformat()
        doc["extractedText"] = result.get("extracted_text", "")
        doc["entities"] = result.get("entities", [])
        doc["confidence"] = result.get("confidence", 0.0)
        doc["metadata"]["trace_id"] = result.get("trace_id")
        
        return {
            "document_id": document_id,
            "trace_id": result.get("trace_id"),
            "status": "completed",
            "confidence": result.get("confidence", 0.0),
            "duration_ms": result.get("duration_ms", 0)
        }
        
    except Exception as e:
        # Update status to error
        if document_id in DOCUMENT_STORE:
            DOCUMENT_STORE[document_id]["status"] = "error"
            DOCUMENT_STORE[document_id]["metadata"]["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(require_permissions(["delete"]))
):
    """Delete a document"""
    try:
        if document_id not in DOCUMENT_STORE:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = DOCUMENT_STORE[document_id]
        file_path = doc["metadata"]["file_path"]
        
        # Delete file from filesystem
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove from document store
        del DOCUMENT_STORE[document_id]
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_document_stats(current_user: dict = Depends(get_current_user)):
    """Get document statistics"""
    try:
        documents = list(DOCUMENT_STORE.values())
        
        total_documents = len(documents)
        total_size = sum(doc["size"] for doc in documents)
        status_counts = {}
        
        for doc in documents:
            status = doc["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_documents": total_documents,
            "total_size_bytes": total_size,
            "status_distribution": status_counts,
            "average_confidence": sum(doc.get("confidence", 0) or 0 for doc in documents) / max(total_documents, 1)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
